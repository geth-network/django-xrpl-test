from django_filters import FilterSet, CharFilter

from xrpl_app.models import PaymentTransaction


class PaymentsFilter(FilterSet):
    account = CharFilter(field_name='account__hash',
                         lookup_expr="exact")
    account__contains = CharFilter(field_name="account__hash",
                                   lookup_expr="contains")
    destination = CharFilter(field_name='destination__hash',
                             lookup_expr="exact")
    destination__contains = CharFilter(field_name="destination__hash",
                                       lookup_expr="contains")
    issuer = CharFilter(field_name="asset_info__issuer__hash",
                        lookup_expr="exact")
    issuer__contains = CharFilter(field_name="asset_info__issuer__hash",
                                  lookup_expr="contains")
    currency = CharFilter(field_name="asset_info__currency",
                          lookup_expr="exact")
    currency__contains = CharFilter(field_name="asset_info__currency",
                                    lookup_expr="contains")

    class Meta:
        model = PaymentTransaction
        fields = {
            'ledger_idx': ['exact', 'lt', 'gt', 'lte', 'gte'],
            'destination_tag': ['exact', 'lt', 'gt', 'lte', 'gte'],
            'hash': ['exact', 'contains'],
            'amount': ['exact'],

        }
