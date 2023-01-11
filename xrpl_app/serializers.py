from rest_framework import serializers

from xrpl_app.models import (AssetInfo, Currency, PaymentTransaction,
                             XRPLAccount)


class RequestLastPaymentsSerializer(serializers.Serializer):
    url = serializers.URLField()
    account = serializers.CharField(max_length=35)


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
            issuer=ret["issuer"], currency=ret["currency"]
        )
        return obj_assets


class ListPaymentSerializer(serializers.ModelSerializer):
    account = XRPLAccountSerializer()
    destination = XRPLAccountSerializer()
    asset_info = AssetInfoSerializer()

    class Meta:
        model = PaymentTransaction
        fields = "__all__"
