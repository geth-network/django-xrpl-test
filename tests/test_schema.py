import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_get_transactions(client, transaction, schema_tester):
    response = client.get(reverse("paymenttransaction-list"),
                          HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)


@pytest.mark.django_db
def test_detail_transaction(client, transaction, schema_tester):
    response = client.get(
        reverse("paymenttransaction-detail", args=[transaction.pk]),
        HTTP_HOST="localhost:8001",
    )
    schema_tester.validate_response(response)


@pytest.mark.django_db
def test_get_xrpl_accounts(client, transaction, schema_tester):
    response = client.get(reverse("xrplaccount-list"),
                          HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)


@pytest.mark.django_db
def test_get_xrpl_accounts(client, transaction, schema_tester):
    response = client.get(reverse("xrplaccount-list"),
                          HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)


@pytest.mark.django_db
def test_get_assets(client, transaction, schema_tester):
    response = client.get(reverse("assetinfo-list"),
                          HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
