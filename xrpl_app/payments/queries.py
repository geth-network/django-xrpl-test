import logging
from functools import lru_cache
from typing import Dict, Tuple

from django.db.models import QuerySet

from xrpl_app.models import AssetInfo, PaymentTransaction, XRPLAccount
from .data import XRPTransaction, Amount


logger = logging.getLogger(__name__)


class AccountsQuery:
    model = XRPLAccount

    def __init__(self):
        self.cache = {}

    def setup_cache(self, accounts: set) -> None:
        """
        Select already exist accounts and create new accounts
        Args:
            accounts: all accounts hashes from successful payments

        Returns:
            None
        """
        exists_accounts_set = self.model.objects.filter(hash__in=accounts)
        self.cache = {obj.hash: obj for obj in exists_accounts_set}
        isnt_exists_accounts = accounts - set(self.cache)
        if isnt_exists_accounts:
            new_accounts = self.model.objects.bulk_create(
                [XRPLAccount(hash=val) for val in isnt_exists_accounts]
            )
            for acc in new_accounts:
                self.cache[acc.hash] = acc

    def get_or_set(self, item: str) -> QuerySet[XRPLAccount]:
        obj = self.cache.get(item)
        if not obj:
            source = self.model.objects.create(hash=item)
            self.cache[item] = source
        return obj

    def update_accounts(self, accounts: QuerySet[XRPLAccount]) -> None:
        accounts_data = {obj.hash: obj for obj in accounts}
        self.cache.update(accounts_data)


class AssetsQuery:
    model = AssetInfo

    @lru_cache
    def get_asset_info(self, issuer: str | QuerySet[XRPLAccount], currency: str):
        obj, _ = self.model.objects.get_or_create(
            issuer=issuer, currency=currency
        )
        return obj

    @lru_cache
    def get_default_asset(self):
        obj = self.model.get_default_asset()
        return obj


class PaymentsQuery:

    def __init__(self):
        self.accounts = AccountsQuery()
        self.assets = AssetsQuery()

    @staticmethod
    def parse_payments(payments: Dict[str, XRPTransaction]) -> Tuple[set, list]:
        """
        Collect info about accounts that already exist in DB.
        Collect new payments to store them in DB.
        Args:
            payments (dict): successful payments from an account history

        Returns:
            set: all accounts hashes from payments
            list: target payments

        """
        exists_payments = (
            set(PaymentTransaction.objects.filter(hash__in=payments).
                values_list('hash', flat=True))
        )
        target_data, acc_hashes = [], set()
        for payment_hash, payment in payments.items():
            if payment_hash in exists_payments:
                continue
            acc_hashes.add(payment.source)
            acc_hashes.add(payment.destination)
            amount = payment.amount
            if isinstance(amount, Amount):
                acc_hashes.add(amount.issuer)
            target_data.append(payment)
        return acc_hashes, target_data

    def save_data(self, transactions: list) -> QuerySet[PaymentTransaction]:
        """
        Prepare account payments data and store it to the database
        Args:
            transactions (list): account history data retrieved from XRP server

        Returns:
            list: saved payments represented as a Django ORM objects
        """
        payments = self.filter_input_data(transactions)
        logger.info(f"Found {len(payments)} payments")
        acc_hashes, target_data = self.parse_payments(payments)
        self.accounts.setup_cache(acc_hashes)
        insert_data = []
        for payment in target_data:
            insert_obj = self.prepare_payment_query(payment)
            insert_data.append(insert_obj)
        obj = PaymentTransaction.objects.bulk_create(insert_data)
        return obj

    @staticmethod
    def filter_input_data(transactions: list) -> Dict[str, XRPTransaction]:
        """

        Args:
            transactions (list): account history data retrieved from XRP server

        Returns:
            dict: data on successful payments
        """
        payments = {}
        for elem in transactions:
            elem = XRPTransaction(**elem)
            if not (elem.is_successful and elem.is_validated and elem.is_it_payment):
                continue
            payments[elem.hash] = elem
        return payments

    def prepare_payment_query(self, payment: XRPTransaction) -> PaymentTransaction:
        source = self.accounts.get_or_set(payment.source)
        dest = self.accounts.get_or_set(payment.destination)
        amount = payment.amount
        if isinstance(amount, str):
            asset = self.assets.get_default_asset()
        else:
            issuer = self.accounts.get_or_set(amount.issuer)
            asset = self.assets.get_asset_info(issuer,
                                               amount.currency)
        obj = PaymentTransaction(
            account=source, destination=dest, ledger_idx=payment.ledger_index,
            destination_tag=payment.destination_tag, amount=payment.amount_value,
            hash=payment.hash, fee=payment.fee, asset_info=asset
        )
        return obj
