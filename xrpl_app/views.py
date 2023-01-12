import logging

from django.db import transaction
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.mixins import RetrieveModelMixin, CreateModelMixin, \
    ListModelMixin
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet
from xrpl.account import get_account_transactions
from xrpl.clients import JsonRpcClient
from httpx import NetworkError, TimeoutException

from xrpl_app.filters import PaymentsFilter, AccountsFilter, AssetsFilter
from xrpl_app.models import PaymentTransaction, XRPLAccount, AssetInfo, Currency
from xrpl_app.serializers import ListPaymentSerializer, \
    RequestLastPaymentsSerializer, XRPLAccountSerializer, AssetInfoSerializer
from xrpl_app.exceptions import XRPLServiceUnavailable

logger = logging.getLogger(__name__)


class AccountsViewSet(ListModelMixin,
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
    permission_classes = (AllowAny, )
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
        try:
            transactions = get_account_transactions(data["account"], client)
        except (TimeoutException, NetworkError) as err:
            logger.exception("XRPL request error")
            raise XRPLServiceUnavailable()
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

    def save_data(self, transactions: list) -> list:
        result = []
        payments = self.filter_payments(transactions)
        logger.info(f"Found {len(payments)} payments")
        exists_payments = (
            set(PaymentTransaction.objects.filter(hash__in=payments).
                values_list('hash', flat=True))
        )
        with transaction.atomic():
            insert_data = []
            for trans_hash in payments:
                if trans_hash in exists_payments:
                    continue
                payment = payments[trans_hash]
                insert_obj = self.prepare_payment_query(payment)
                insert_data.append(insert_obj)
            obj = PaymentTransaction.objects.bulk_create(insert_data)
            result.extend(obj)
        return result

    def prepare_payment_query(self, data: dict):
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
        amount = data["Amount"]
        if isinstance(amount, str):
            insert_data["amount"] = amount
            default_asset = cache.get("asset")
            if not default_asset:
                default_asset = AssetInfo.get_default_asset()
                cache.set("asset", default_asset)
            insert_data["asset_info"] = default_asset
        elif isinstance(amount, dict):
            insert_data["amount"] = amount["value"]
            issuer, _ = XRPLAccount.objects.get_or_create(hash=amount["issuer"])
            currency, _ = Currency.objects.get_or_create(name=amount["currency"])
            asset, _ = AssetInfo.objects.get_or_create(issuer=issuer,
                                                       currency=currency)
            insert_data["asset_info"] = asset

        else:
            raise ValueError(f"Invalid amount format: {type(amount).__name__}")
        obj = PaymentTransaction(**insert_data)
        return obj
