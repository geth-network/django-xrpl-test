from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from xrpl_app.filters import PaymentsFilter
from xrpl_app.models import PaymentTransaction
from xrpl_app.serializers import ListCreatePaymentSerializer

"""{"hash": "2", "account": "2", "destination": "2", 
 "asset_info": {"issuer": "2", "currency": "BTC", "amount": "5000"},
"ledger_idx": "5", "destination_tag": "6", "fee": 7}"""


class ListCreatePaymentsView(generics.ListCreateAPIView):
    queryset = PaymentTransaction.objects.all().select_related(
        "account", "destination", "asset_info", "asset_info__issuer"
    )
    serializer_class = ListCreatePaymentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ("account__hash", "destination__hash", "hash")
    ordering_fields = ("ledger_idx",)
    filterset_fields = '__all__'
    filterset_class = PaymentsFilter

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


