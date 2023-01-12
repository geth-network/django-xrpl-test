import logging

from django.db import transaction
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet
from xrpl.account import get_account_transactions
from xrpl.clients import JsonRpcClient
from httpx import NetworkError, TimeoutException

from xrpl_app import filters
from xrpl_app import models
from xrpl_app import serializers
from xrpl_app.exceptions import XRPLServiceUnavailable

logger = logging.getLogger(__name__)


class AccountsViewSet(mixins.ListModelMixin,
                      GenericViewSet):
    queryset = models.XRPLAccount.objects.all()
    serializer_class = serializers.XRPLAccountSerializer
    filterset_class = filters.AccountsFilter


class AssetsInfoViewSet(mixins.ListModelMixin,
                        GenericViewSet):
    queryset = models.AssetInfo.objects.select_related("issuer")
    serializer_class = serializers.AssetInfoSerializer
    filterset_class = filters.AssetsFilter


class PaymentsViewSet(mixins.RetrieveModelMixin,
                      mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      GenericViewSet):
    queryset = models.PaymentTransaction.objects.select_related(
        "account", "destination", "asset_info",
        "asset_info__issuer"
    )
    permission_classes = (AllowAny, )
    filterset_class = filters.PaymentsFilter

    def get_serializer_class(self):
        if self.action == "create":
            return serializers.RequestLastPaymentsSerializer
        elif self.action in ["list", "retrieve"]:
            return serializers.ListPaymentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        client = JsonRpcClient(data["url"])
        try:
            trans_data = get_account_transactions(data["account"], client)
        except (TimeoutException, NetworkError) as err:
            logger.exception("XRPL request error")
            raise XRPLServiceUnavailable()
        with transaction.atomic():
            objects = self.save_data(trans_data)
        result = serializers.ListPaymentSerializer(instance=objects, many=True)
        return Response(result.data, status=201)

    @staticmethod
    def filter_payments(transactions: list) -> dict:
        payments = {}
        for elem in transactions:
            if elem["meta"]["TransactionResult"] != "tesSUCCESS" or not elem["validated"]:
                continue
            tx = elem["tx"]
            if tx["TransactionType"] != "Payment":
                continue
            payments[tx["hash"]] = tx
        return payments

    def save_data(self, transactions: list) -> list:
        result = []
        payments = self.filter_payments(transactions)
        logger.info(f"Found {len(payments)} payments")
        exists_payments = (
            set(models.PaymentTransaction.objects.filter(hash__in=payments).
                values_list('hash', flat=True))
        )
        target_data, acc_hashes = [], set()
        for payment_hash, payment in payments.items():
            if payment_hash in exists_payments:
                continue
            acc_hashes.add(payment["Account"])
            acc_hashes.add(payment["Destination"])
            amount = payment["Amount"]
            if isinstance(amount, dict):
                acc_hashes.add(amount["issuer"])
            target_data.append(payment)

        exists_accounts_set = models.XRPLAccount.objects.filter(hash__in=acc_hashes)
        exists_accounts = {obj.hash: obj for obj in exists_accounts_set}
        isnt_exists_accounts = acc_hashes - set(exists_accounts)
        new_accounts = models.XRPLAccount.objects.bulk_create(
            [models.XRPLAccount(hash=val) for val in isnt_exists_accounts]
        )
        for acc in new_accounts:
            exists_accounts[acc.hash] = acc
        insert_data = []
        assets = {}
        for payment in target_data:
            insert_obj = self.prepare_payment_query(payment, assets,
                                                    exists_accounts)
            insert_data.append(insert_obj)
        obj = models.PaymentTransaction.objects.bulk_create(insert_data)
        result.extend(obj)
        return result

    @staticmethod
    def prepare_payment_query(data: dict, assets: dict, accounts: dict):
        source = accounts.get(data["Account"])
        if not source:
            source = models.XRPLAccount.objects.create(hash=data["Account"])
            accounts[source.hash] = source
        dest = accounts.get(data["Destination"])
        if not dest:
            dest = models.XRPLAccount.objects.create(hash=data["Destination"])
            accounts[dest.hash] = dest
        amount = data["Amount"]
        if isinstance(amount, str):
            asset = models.AssetInfo.get_default_asset()
        elif isinstance(amount, dict):
            issuer = accounts.get(amount["issuer"])
            if not issuer:
                issuer = models.XRPLAccount.objects.create(hash=amount["issuer"])
                accounts[issuer.hash] = issuer
            asset_key = (amount["issuer"], amount["currency"])
            asset = assets.get(asset_key)
            if not asset:
                asset, _ = models.AssetInfo.objects.get_or_create(
                    issuer=issuer, currency=amount["currency"]
                )
                assets[asset_key] = asset
        else:
            raise ValueError(f"Invalid amount format: {type(amount).__name__}")
        obj = models.PaymentTransaction(
            account=source, destination=dest, ledger_idx=data["ledger_index"],
            destination_tag=data.get("DestinationTag"),
            hash=data["hash"], fee=data["Fee"], asset_info=asset
        )
        return obj
