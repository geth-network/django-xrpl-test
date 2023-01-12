from collections import OrderedDict

from rest_framework import serializers
from xrpl_app import models


class RequestLastPaymentsSerializer(serializers.Serializer):
    url = serializers.URLField()
    account = serializers.CharField(max_length=35)


class XRPLAccountSerializer(serializers.ModelSerializer):
    hash = serializers.CharField(max_length=35)

    class Meta:
        model = models.XRPLAccount
        fields = "__all__"
        read_only_fields = ("hash", )


class AssetInfoSerializer(serializers.ModelSerializer):
    issuer = XRPLAccountSerializer()

    class Meta:
        model = models.AssetInfo
        fields = ("issuer", "currency")
        read_only_fields = fields

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["issuer"] = instance.issuer_id
        return ret


class ListPaymentSerializer(serializers.ModelSerializer):
    account = XRPLAccountSerializer()
    destination = XRPLAccountSerializer()
    asset_info = AssetInfoSerializer()

    class Meta:
        model = models.PaymentTransaction
        fields = "__all__"
        read_only_fields = ("account", "destination", "asset_info", "ledger_idx",
                            "destination_tag", "hash", "amount", "fee")

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["account"] = instance.account_id
        ret["destination"] = instance.destination_id
        ret["asset_info"] = OrderedDict(
            issuer=instance.asset_info.issuer_id,
            currency=instance.asset_info.currency
        )
        return ret
