import logging

from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework import permissions, viewsets
from xrpl.account import get_account_transactions
from xrpl.clients import JsonRpcClient
from httpx import NetworkError, TimeoutException

from xrpl_app import filters, models, serializers
from xrpl_app.exceptions import XRPLServiceUnavailable
from xrpl_app.payments import PaymentsQuery


logger = logging.getLogger(__name__)


class AccountsViewSet(mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    queryset = models.XRPLAccount.objects.all()
    serializer_class = serializers.XRPLAccountSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.AccountsFilter


class AssetsInfoViewSet(mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    queryset = models.AssetInfo.objects.select_related("issuer")
    serializer_class = serializers.AssetInfoSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.AssetsFilter


class PaymentsViewSet(mixins.RetrieveModelMixin,
                      mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    queryset = models.PaymentTransaction.objects.select_related(
        "account", "destination", "asset_info",
        "asset_info__issuer"
    )
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (permissions.AllowAny, )
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
            objects = PaymentsQuery(data["account"]).save_data(trans_data)
        result = serializers.ListPaymentSerializer(instance=objects, many=True)
        return Response(result.data, status=201)
