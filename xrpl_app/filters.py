from django_filters import BooleanFilter, CharFilter, FilterSet, NumberFilter

from xrpl_app.models import PaymentTransaction, XRPLAccount, AssetInfo


class AssetsFilter(FilterSet):
    issuer = CharFilter(field_name="issuer__hash", lookup_expr="exact")
    issuer__contains = CharFilter(field_name="issuer__hash",
                                  lookup_expr="contains")
    currency = CharFilter(field_name="currency",
                          lookup_expr="exact")
    currency__contains = CharFilter(field_name="currency__name",
                                    lookup_expr="contains")

    class Meta:
        model = AssetInfo
        fields = "__all__"


class AccountsFilter(FilterSet):
    class Meta:
        model = XRPLAccount
        fields = {
            "hash": ["exact", "contains"],
        }


class PaymentsFilter(FilterSet):
    account = CharFilter(field_name="account__hash", lookup_expr="exact")
    account__contains = CharFilter(field_name="account__hash", lookup_expr="contains")
    destination = CharFilter(field_name="destination__hash", lookup_expr="exact")
    destination__contains = CharFilter(
        field_name="destination__hash", lookup_expr="contains"
    )
    issuer = CharFilter(field_name="asset_info__issuer__hash", lookup_expr="exact")
    issuer__contains = CharFilter(
        field_name="asset_info__issuer__hash", lookup_expr="contains"
    )
    currency = CharFilter(field_name="asset_info__currency__name", lookup_expr="exact")
    currency__contains = CharFilter(
        field_name="asset_info__currency__name", lookup_expr="contains"
    )
    destination_tag = NumberFilter(field_name="destination_tag", lookup_expr="exact")
    destination_tag__isnull = BooleanFilter(
        field_name="destination_tag", lookup_expr="isnull"
    )

    class Meta:
        model = PaymentTransaction
        fields = {
            "ledger_idx": ["exact", "lt", "gt", "lte", "gte"],
            "destination_tag": ["exact"],
            "hash": ["exact", "contains"],
            "amount": ["exact"],
        }
