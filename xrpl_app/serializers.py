from django.conf import settings
from rest_framework import serializers

from xrpl_app.models import (
    PaymentTransaction, XRPLAccount, AssetInfo,
    Currency
)


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = "__all__"

    def to_internal_value(self, data):
        instance, _ = self.Meta.model.objects.get_or_create(name=data)
        return instance

    def to_representation(self, instance):
        return instance.name


class XRPLAccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = XRPLAccount
        fields = "__all__"

    def to_internal_value(self, data):
        instance, _ = self.Meta.model.objects.get_or_create(hash=data)
        return instance

    def to_representation(self, instance):
        return instance.hash


class AssetInfoSerializer(serializers.ModelSerializer):
    issuer = XRPLAccountSerializer()
    currency = CurrencySerializer()

    class Meta:
        model = AssetInfo
        fields = ("issuer", "currency")

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)
        obj_assets, _ = self.Meta.model.objects.get_or_create(
            issuer=ret['issuer'], currency=ret['currency']
        )
        return obj_assets


class ListCreatePaymentSerializer(serializers.ModelSerializer):
    account = XRPLAccountSerializer()
    destination = XRPLAccountSerializer()
    asset_info = AssetInfoSerializer()

    class Meta:
        model = PaymentTransaction
        fields = "__all__"

    def create(self, validated_data):
        account = validated_data.pop("account")
        dest_acc = validated_data.pop("destination")
        asset_obj = validated_data.pop("asset_info")
        payment = PaymentTransaction.objects.create(
            account=account, destination=dest_acc,
            asset_info=asset_obj, **validated_data
        )
        return payment
