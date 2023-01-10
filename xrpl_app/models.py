from django.contrib import admin
from django.db import models
from django.conf import settings


class XRPLAccount(models.Model):
    hash = models.CharField(max_length=35, primary_key=True)

    class Meta:
        verbose_name_plural = "XRPL Accounts"
        verbose_name = "XRPL Account"

    def __str__(self):
        return self.hash

    @staticmethod
    def get_default_account():
        obj, _ = XRPLAccount.objects.get_or_create(
            hash=settings.DEFAULT_XRPL_ACCOUNT
        )
        return obj


class Currency(models.Model):
    name = models.CharField(max_length=40, primary_key=True)

    @staticmethod
    def get_default_currency():
        obj, _ = Currency.objects.get_or_create(
            name=settings.DEFAULT_XRPL_ASSET
        )
        return obj


class AssetInfo(models.Model):
    issuer = models.ForeignKey(XRPLAccount, on_delete=models.CASCADE,
                               default=XRPLAccount.get_default_account)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE,
                                 default=Currency.get_default_currency)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["issuer", "currency"],
                name="unique_asset_issuer_currency"
            )
        ]
        verbose_name_plural = "Assets Info"
        verbose_name = "Asset Info"

    def __str__(self):
        return f"{self.currency}.{self.issuer}"


class PaymentTransaction(models.Model):
    account = models.ForeignKey(XRPLAccount, on_delete=models.CASCADE,
                                related_name="account")
    destination = models.ForeignKey(XRPLAccount, on_delete=models.CASCADE,
                                    related_name="destination")
    asset_info = models.ForeignKey(AssetInfo, on_delete=models.CASCADE,
                                   related_name="asset_info")
    ledger_idx = models.PositiveBigIntegerField()
    destination_tag = models.PositiveBigIntegerField(null=True)
    hash = models.CharField(max_length=64, primary_key=True)
    amount = models.CharField(max_length=24)
    fee = models.CharField(max_length=24)

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
