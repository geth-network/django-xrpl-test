from urllib.parse import urlencode
from uuid import uuid4

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_get_assets_issuer_exact_match(client, transaction, schema_tester):
    url = reverse("assetinfo-list")
    url += f"?{urlencode({'issuer': transaction.asset_info.issuer_id})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 1


@pytest.mark.django_db
def test_get_assets_issuer_exact_empty(client, transaction, schema_tester):
    url = reverse("assetinfo-list")
    url += f"?{urlencode({'issuer': uuid4().hex})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 0


@pytest.mark.django_db
def test_get_assets_issuer_contains_match(client, transaction, schema_tester):
    partial_id = transaction.asset_info.issuer_id[:-1]
    url = reverse("assetinfo-list")
    url += f"?{urlencode({'issuer__contains': partial_id})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 1


@pytest.mark.django_db
def test_get_assets_issuer_contains_empty(client, transaction, schema_tester):
    url = reverse("assetinfo-list")
    url += f"?{urlencode({'issuer__contains': uuid4().hex})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 0


@pytest.mark.django_db
def test_get_assets_currency_exact_match(client, transaction, schema_tester):
    url = reverse("assetinfo-list")
    url += f"?{urlencode({'currency': transaction.asset_info.currency})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 1


@pytest.mark.django_db
def test_get_assets_currency_exact_empty(client, transaction, schema_tester):
    url = reverse("assetinfo-list")
    url += f"?{urlencode({'currency': uuid4().hex})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 0


@pytest.mark.django_db
def test_get_assets_currency_contains_match(client, transaction,
                                            schema_tester):
    partial_id = transaction.asset_info.currency[:-1]
    url = reverse("assetinfo-list")
    url += f"?{urlencode({'currency__contains': partial_id})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 1


@pytest.mark.django_db
def test_get_assets_currency_contains_empty(client, transaction,
                                            schema_tester):
    url = reverse("assetinfo-list")
    url += f"?{urlencode({'currency__contains': uuid4().hex})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 0
