from django_filters import BooleanFilter, CharFilter, FilterSet, NumberFilter

from xrpl_app.models import AssetInfo, PaymentTransaction, XRPLAccount


class AssetsFilter(FilterSet):
    issuer = CharFilter(field_name="issuer__hash", lookup_expr="exact")
    issuer__contains = CharFilter(field_name="issuer__hash",
                                  lookup_expr="contains")

    class Meta:
        model = AssetInfo
        fields = {
            "currency": ["exact", "contains"],
        }


class AccountsFilter(FilterSet):
    class Meta:
        model = XRPLAccount
        fields = {
            "hash": ["exact", "contains"],
        }


class PaymentsFilter(FilterSet):
    account = CharFilter(field_name="account__hash", lookup_expr="exact")
    account__contains = CharFilter(field_name="account__hash",
                                   lookup_expr="contains")
    destination = CharFilter(field_name="destination__hash",
                             lookup_expr="exact")
    destination__contains = CharFilter(
        field_name="destination__hash", lookup_expr="contains"
    )
    issuer = CharFilter(field_name="asset_info__issuer__hash",
                        lookup_expr="exact")
    issuer__contains = CharFilter(
        field_name="asset_info__issuer__hash", lookup_expr="contains"
    )
    currency = CharFilter(field_name="asset_info__currency",
                          lookup_expr="exact")
    currency__contains = CharFilter(
        field_name="asset_info__currency", lookup_expr="contains"
    )
    destination_tag = NumberFilter(field_name="destination_tag",
                                   lookup_expr="exact")
    destination_tag__isnull = BooleanFilter(
        field_name="destination_tag", lookup_expr="isnull"
    )

    class Meta:
        model = PaymentTransaction
        fields = {
            "ledger_idx": ["exact"],
            "hash": ["exact", "contains"],
        }
