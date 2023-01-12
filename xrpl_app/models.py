from functools import cache

from django.conf import settings
from django.contrib import admin
from django.db import models

from xrpl_app.validators import validate_numeric


class XRPLAccount(models.Model):
    # https://xrpl.org/accounts.html#addresses
    hash = models.CharField(max_length=35, primary_key=True)

    class Meta:
        verbose_name_plural = "XRPL Accounts"
        verbose_name = "XRPL Account"

    def __str__(self):
        return self.hash

    @staticmethod
    @cache
    def get_default_account():
        obj, _ = XRPLAccount.objects.get_or_create(
            hash=settings.DEFAULT_XRPL_ACCOUNT
        )
        return obj



class AssetInfo(models.Model):
    issuer = models.ForeignKey(XRPLAccount, on_delete=models.CASCADE)
    # https://xrpl.org/currency-formats.html#nonstandard-currency-codes
    currency = models.CharField(max_length=40,
                                default=settings.DEFAULT_XRPL_ASSET)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["issuer", "currency"], name="unique_issuer_currency"
            )
        ]
        verbose_name_plural = "Assets Info"
        verbose_name = "Asset Info"

    @staticmethod
    @cache
    def get_default_asset():
        obj, _ = AssetInfo.objects.get_or_create(
            issuer=XRPLAccount.get_default_account(),
        )
        return obj

    def __str__(self):
        return f"{self.currency}.{self.issuer}"


class PaymentTransaction(models.Model):
    account = models.ForeignKey(
        XRPLAccount, on_delete=models.CASCADE, related_name="account"
    )
    destination = models.ForeignKey(
        XRPLAccount, on_delete=models.CASCADE, related_name="destination"
    )
    asset_info = models.ForeignKey(
        AssetInfo, on_delete=models.CASCADE, related_name="asset_info"
    )
    # https://xrpl.org/basic-data-types.html#ledger-index
    ledger_idx = models.PositiveBigIntegerField()
    destination_tag = models.PositiveBigIntegerField(null=True)
    # https://xrpl.org/basic-data-types.html#hashes
    hash = models.CharField(max_length=64, primary_key=True)
    # https://xrpl.org/currency-formats.html
    amount = models.CharField(max_length=24, validators=[validate_numeric])
    fee = models.CharField(max_length=24, validators=[validate_numeric])

    class Meta:
        verbose_name_plural = "Payment Transactions"
        verbose_name = "Payment Transaction"

    def __str__(self):
        return self.hash

    @property
    @admin.display(description="Hash")
    def transaction_hash(self):
        trans_hash = self.hash
        if len(trans_hash) > 10:
            return f"{trans_hash[:10]}…"
        return trans_hash

    @property
    @admin.display(description="Source Hash")
    def account_hash(self):
        src_hash = self.account.hash
        if len(src_hash) > 10:
            return f"{src_hash[:10]}…"
        return src_hash

    @property
    @admin.display(description="Destination Hash")
    def dest_hash(self):
        dest_hash = self.destination.hash
        if len(dest_hash) > 10:
            return f"{dest_hash[:10]}…"
        return dest_hash
