from django.contrib import admin

from xrpl_app.models import AssetInfo, PaymentTransaction, XRPLAccount


@admin.register(AssetInfo)
class AssetInfoAdmin(admin.ModelAdmin):
    list_display = ("issuer", "currency")
    search_fields = ("issuer", "currency")


@admin.register(XRPLAccount)
class XRPLAccountAdmin(admin.ModelAdmin):
    list_display = ("hash",)
    search_fields = ("hash",)


@admin.register(PaymentTransaction)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "transaction_hash", "ledger_idx", "account_hash",
        "dest_hash", "destination_tag", "amount", "fee",
    )

    ordering = ("ledger_idx",)
    list_select_related = True
    search_fields = ("account__hash", "destination__hash", "hash")
