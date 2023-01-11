import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from openapi_tester.schema_tester import SchemaTester
from rest_framework.test import APIClient

from xrpl_app.models import PaymentTransaction


@pytest.fixture
def payment_payload():
    payload = {
        "hash": "ABCD",
        "account": "BCDEF",
        "destination": "TESTACC",
        "asset_info": {"issuer": "BCDEF", "currency": "USD"},
        "amount": "5000",
        "ledger_idx": 1,
        "fee": "1",
        "destination_tag": 12,
    }
    return payload


@pytest.fixture
def schema_tester():
    return SchemaTester(schema_file_path=settings.API_SCHEMA_FILEPATH)


@pytest.fixture(scope="session")
def fill_db(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command("loaddata", settings.DB_DATA_FIXTURE)


@pytest.fixture(scope="session")
def transaction(fill_db, django_db_blocker):
    with django_db_blocker.unblock():
        obj = PaymentTransaction.objects.all().first()
    return obj
