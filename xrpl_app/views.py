import logging

from django.db import transaction
from django.apps import apps
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import (ListAPIView, ListCreateAPIView,
                                     RetrieveAPIView, CreateAPIView)
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from xrpl.clients import JsonRpcClient
from xrpl.account import get_account_transactions

from xrpl_app.filters import PaymentsFilter
from xrpl_app.models import PaymentTransaction, XRPLAccount, AssetInfo, Currency
from xrpl_app.serializers import ListCreatePaymentSerializer, \
    RequestLastPaymentsSerializer


logger = logging.getLogger(__name__)


class ListCreatePaymentsView(ListAPIView):
    queryset = PaymentTransaction.objects.select_related(
        "account", "destination", "asset_info",
        "asset_info__issuer", "asset_info__currency",
    )
    serializer_class = ListCreatePaymentSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ("account__hash", "destination__hash", "hash")
    ordering_fields = ("ledger_idx",)
    filterset_fields = "__all__"
    filterset_class = PaymentsFilter


class RetrievePaymentView(RetrieveAPIView):
    queryset = PaymentTransaction.objects.select_related(
        "account", "destination", "asset_info",
        "asset_info__issuer", "asset_info__currency",
    )
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ListCreatePaymentSerializer


class ParseAndStoreLastPayments(CreateAPIView):
    queryset = PaymentTransaction.objects.select_related(
        "account", "destination", "asset_info",
        "asset_info__issuer", "asset_info__currency",
    )
    serializer_class = RequestLastPaymentsSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        client = JsonRpcClient(data["url"])
        transactions = get_account_transactions(data["account"], client)
        objects = self.actualize_history(transactions)
        result = ListCreatePaymentSerializer(instance=objects, many=True).data
        return Response(result, status=200)

    @staticmethod
    def get_payment(data: dict):
        try:
            obj = PaymentTransaction.objects.get(hash=data["hash"])
        except PaymentTransaction.DoesNotExist:
            obj = None
        return obj

    def actualize_history(self, transactions: list) -> list:
        target = [
            tx["tx"]
            for tx in transactions
            if tx["tx"]["TransactionType"] == "Payment"
            and tx["validated"]
            and tx["meta"]["TransactionResult"] == "tesSUCCESS"
        ]
        result = []
        if target:
            logger.info(f"Found {len(target)} payments")
            for trans in target:
                payment = self.get_payment(trans)
                if not payment:
                    payment = self.db_transaction(trans)
                result.append(payment)
        return result

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
        amount = data["Amount"]
        if isinstance(amount, str):
            insert_data["amount"] = amount
            app_conf = apps.get_app_config("xrpl_app")
            insert_data["asset_info"] = app_conf.default_asset
        elif isinstance(amount, dict):
            insert_data["amount"] = amount["value"]
            issuer, _ = XRPLAccount.objects.get_or_create(hash=amount["issuer"])
            currency, _ = Currency.objects.get_or_create(
                name=amount["currency"])
            asset, _ = AssetInfo.objects.get_or_create(issuer=issuer,
                                                       currency=currency)
            insert_data["asset_info"] = asset

        else:
            raise ValueError(f"Invalid amount format: {type(amount).__name__}")
        obj = self.get_queryset().create(**insert_data)
        return obj
