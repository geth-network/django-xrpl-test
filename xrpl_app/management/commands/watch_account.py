import asyncio
import logging
from typing import List, Tuple

from asgiref.sync import sync_to_async
import xrpl
from xrpl.core import addresscodec
from xrpl.models import Subscribe, StreamParameter
from xrpl.asyncio.clients import AsyncWebsocketClient
from xrpl.asyncio.account import get_account_transactions
from django.db import transaction
from django.core.management.base import BaseCommand

from xrpl_app.models import PaymentTransaction, XRPLAccount, AssetInfo


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Watch success payments by account from server by account and fill the DB
    """
    tasks_limit = 100
    help = ''  # TODO

    def add_arguments(self, parser):
        parser.add_argument(
            '-t',
            '--target_account',
            type=self.xaddress2address,
            required=True,
            help='account classic address (classic- or X-format)',
        )
        parser.add_argument(
            '-url',
            type=str,
            required=True,
            help='rippled server url',
        )

    def handle(self, *args, **options):
        account = options["target_account"]
        url = options["url"]
        asyncio.run(self.listen_account(account, url))

    @staticmethod
    def xaddress2address(addr: str) -> str:
        if not isinstance(addr, str):
            raise ValueError(f"Expected type 'str', "
                             f"got {type(addr).__name__} instead.")
        if addresscodec.is_valid_xaddress(addr):
            classic_addr, _, _ = addresscodec.xaddress_to_classic_address(addr)
        elif addresscodec.is_valid_classic_address(addr):
            classic_addr = addr
        else:
            raise ValueError("Invalid address format")
        return classic_addr

    async def listen_account(self, account: str, url: str) -> None:
        async with AsyncWebsocketClient(url) as client:
            transactions = await get_account_transactions(account, client)
            await self.actualize_history(transactions)
            await client.send(Subscribe(
                streams=[StreamParameter.LEDGER], accounts=[account]
            ))
            async for msg in client:
                if msg.get("type") == "transaction":
                    print(f"received new transaction for {account}")
                    msg["tx"] = msg["transaction"]
                    if "ledger_index" in msg:
                        msg["tx"]["ledger_index"] = msg["ledger_index"]
                    await self.actualize_history([msg])

    @staticmethod
    async def is_payment_exists(data: dict) -> Tuple[bool, dict]:
        res = await PaymentTransaction.objects.filter(hash=data['hash']).aexists()
        return res, data

    async def actualize_history(self, transactions: list):
        target = [tx['tx'] for tx in transactions
                  if tx["tx"]["TransactionType"] == "Payment"
                  and tx['validated']
                  and tx['meta']['TransactionResult'] == 'tesSUCCESS']
        select_tasks = set()
        for trans in target:
            select_tasks.add(self.is_payment_exists(trans))

        insert_tasks = set()
        for task in asyncio.as_completed(select_tasks):
            if len(insert_tasks) >= self.tasks_limit:
                await asyncio.wait(insert_tasks,
                                   return_when=asyncio.FIRST_COMPLETED)
            exists, data = await task
            if not exists:
                insert_tasks.add(asyncio.create_task(self.db_transaction(data)))
        if insert_tasks:
            await asyncio.wait(insert_tasks)

    @sync_to_async
    @transaction.atomic
    def db_transaction(self, data: dict):
        source, _ = XRPLAccount.objects.get_or_create(hash=data["Account"])
        dest, _ = XRPLAccount.objects.get_or_create(hash=data["Destination"])
        insert_data = {
            "account": source,
            "destination": dest,
            "ledger_idx": data["ledger_index"],
            "destination_tag": data.get("DestinationTag"),
            "hash": data["hash"],
            "fee": data["Fee"],
        }
        amount = data['Amount']
        if isinstance(amount, str):
            insert_data["amount"] = amount
            default_asset, _ = AssetInfo.objects.get_or_create()
            insert_data["asset_info"] = default_asset
        elif isinstance(amount, dict):
            insert_data["amount"] = amount["value"]
            issuer, _ = XRPLAccount.objects.get_or_create(hash=amount["issuer"])
            asset, _ = AssetInfo.objects.get_or_create(
                issuer=issuer,
                currency=amount["currency"]
            )
            insert_data["asset_info"] = asset

        else:
            raise ValueError("Invalid amount format")
        PaymentTransaction.objects.create(**insert_data)
