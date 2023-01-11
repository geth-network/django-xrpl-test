import logging

from django.apps import apps
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.mixins import RetrieveModelMixin, CreateModelMixin, \
    ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from xrpl.account import get_account_transactions
from xrpl.clients import JsonRpcClient

from xrpl_app.filters import PaymentsFilter, AccountsFilter, AssetsFilter
from xrpl_app.models import PaymentTransaction, XRPLAccount, AssetInfo, Currency
from xrpl_app.serializers import ListPaymentSerializer, \
    RequestLastPaymentsSerializer, XRPLAccountSerializer, AssetInfoSerializer

logger = logging.getLogger(__name__)


class AccountsViewSet(RetrieveModelMixin,
                      ListModelMixin,
                      GenericViewSet):
    queryset = XRPLAccount.objects.all()
    serializer_class = XRPLAccountSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ("hash",)
    filterset_fields = "__all__"
    filterset_class = AccountsFilter


class AssetsInfoViewSet(ListModelMixin,
                        GenericViewSet):
    queryset = AssetInfo.objects.select_related("issuer", "currency")
    serializer_class = AssetInfoSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ("issuer__hash", "currency__name")
    filterset_fields = "__all__"
    filterset_class = AssetsFilter


class PaymentsViewSet(RetrieveModelMixin,
                      CreateModelMixin,
                      ListModelMixin,
                      GenericViewSet):
    queryset = PaymentTransaction.objects.select_related(
        "account", "destination", "asset_info",
        "asset_info__issuer", "asset_info__currency",
    )
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ("account__hash", "destination__hash", "hash")
    ordering_fields = ("ledger_idx",)
    filterset_fields = "__all__"
    filterset_class = PaymentsFilter

    def get_serializer_class(self):
        if self.action == "create":
            return RequestLastPaymentsSerializer
        elif self.action in ["list", "retrieve"]:
            return ListPaymentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        client = JsonRpcClient(data["url"])
        transactions = get_account_transactions(data["account"], client)
        objects = self.save_data(transactions)
        result = ListPaymentSerializer(instance=objects, many=True).data
        return Response(result, status=201)

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

    @staticmethod
    def get_payments_accounts(payments: dict, exists_payments: set):
        accounts = set()
        for trans_hash in payments:
            if trans_hash in exists_payments:
                del payments[trans_hash]
                continue
            payment = payments[trans_hash]
            accounts.add(payment["Account"])
            accounts.add(payment["Destination"])
            accounts.add(payment["Account"])
            amount = payment["Amount"]
            if isinstance(amount, dict):
                accounts.add(amount["issuer"])
        return accounts, payments

    def save_data(self, transactions: list) -> list:
        result = []
        payments = self.filter_payments(transactions)
        logger.info(f"Found {len(payments)} payments")
        exists_payments = (
            set(PaymentTransaction.objects.filter(hash__in=payments).
                values_list('hash', flat=True))
        )
        payments_accounts, target_payments = self.get_payments_accounts(
            payments, exists_payments
        )
        exists_accounts = (
            XRPLAccount.objects.filter(hash__in=payments_accounts)
        )
        inmemory_accounts = {elem.pk: elem for elem in exists_accounts}
        for payment in target_payments:
            payment = self.db_transaction(target_payments[payment],
                                          inmemory_accounts)
            result.append(payment)
        return result

    @transaction.atomic
    def db_transaction(self, data: dict, accounts: dict):
        source = accounts.get(data["Account"])
        if not source:
            source = XRPLAccount.objects.create(hash=data["Account"])
            accounts[data["Account"]] = source
        dest = accounts.get(data["Destination"])
        if not dest:
            dest = XRPLAccount.objects.create(hash=data["Destination"])
            accounts[data["Destination"]] = dest
        insert_data = {
            "account": source,
            "destination": dest,
            "ledger_idx": data["ledger_index"],
            "destination_tag": data.get("DestinationTag"),
            "hash": data["hash"],
            "fee": data["Fee"],
        }
        amount = data["Amount"]
        if isinstance(amount, str):
            insert_data["amount"] = amount
            app_conf = apps.get_app_config("xrpl_app")
            insert_data["asset_info"] = app_conf.default_asset
        elif isinstance(amount, dict):
            insert_data["amount"] = amount["value"]
            issuer = accounts.get(amount["issuer"])
            if not issuer:
                issuer = XRPLAccount.objects.create(hash=amount["issuer"])
                accounts[amount["issuer"]] = issuer
            currency, _ = Currency.objects.get_or_create(
                name=amount["currency"])
            asset, _ = AssetInfo.objects.get_or_create(issuer=issuer,
                                                       currency=currency)
            insert_data["asset_info"] = asset

        else:
            raise ValueError(f"Invalid amount format: {type(amount).__name__}")
        obj = self.get_queryset().create(**insert_data)
        return obj
