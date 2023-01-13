import pytest
from django.conf import settings
from django.core.management import call_command
from openapi_tester.schema_tester import SchemaTester

from xrpl_app.models import PaymentTransaction, XRPLAccount, AssetInfo


@pytest.fixture
def schema_tester():
    return SchemaTester(schema_file_path=settings.API_SCHEMA_FILEPATH)


@pytest.fixture
def fill_db(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command("loaddata", settings.DB_DATA_FIXTURE)


@pytest.fixture
def transaction(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        src1 = XRPLAccount.objects.create(hash="src-src-src")
        dst1 = XRPLAccount.objects.create(hash="dest-dest-dest")
        asset1 = AssetInfo.objects.create(issuer=src1)
        obj1 = PaymentTransaction.objects.create(
            account=src1, destination=dst1, asset_info=asset1,
            ledger_idx=12345, destination_tag=505,
            hash="1234567", amount="1234", fee="555"
        )
        src2 = XRPLAccount.objects.create(hash='some-hash')
        dst2 = XRPLAccount.objects.create(hash="dest")
        asset2 = AssetInfo.objects.create(issuer=src2, currency="UAH")
        obj2 = PaymentTransaction.objects.create(
            account=src2, destination=dst2, asset_info=asset2,
            ledger_idx=54321, destination_tag=None,
            hash="unique-hash", amount="4321", fee="666"
        )
    return obj1
