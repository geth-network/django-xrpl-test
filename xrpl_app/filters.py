from django_filters import FilterSet

from xrpl_app.models import PaymentTransaction


class PaymentsFilter(FilterSet):

    class Meta:
        model = PaymentTransaction
        fields = {
            'account__hash': ['exact', 'icontains'],
            'destination__hash': ['exact', 'icontains'],
            'asset_info__issuer__hash': ['exact', 'icontains'],
            'asset_info__currency': ['exact', 'icontains'],
            'ledger_idx': ['exact', 'lt', 'gt', 'lte', 'gte'],
            'destination_tag': ['exact', 'lt', 'gt', 'lte', 'gte'],
            'hash': ['exact', 'icontains'],
            'amount': ['exact'],

        }
