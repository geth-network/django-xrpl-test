from uuid import uuid4
import pytest
from django.urls import reverse
from urllib.parse import urlencode


@pytest.mark.django_db
def test_get_accounts_hash_exact_match(client, transaction, schema_tester):
    url = f"{reverse('xrplaccount-list')}"
    url += f"?{urlencode({'hash': transaction.account_id})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 1


@pytest.mark.django_db
def test_get_accounts_hash_exact_empty(client, transaction, schema_tester):
    url = f"{reverse('xrplaccount-list')}"
    url += f"?{urlencode({'hash': uuid4().hex})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 0


@pytest.mark.django_db
def test_get_accounts_hash_contains_match(client, transaction, schema_tester):
    partial_id = transaction.account_id[:-1]
    url = reverse("xrplaccount-list")
    url += f"?{urlencode({'hash__contains': partial_id})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 1


@pytest.mark.django_db
def test_get_accounts_hash_contains_empty(client, transaction, schema_tester):
    url = f"{reverse('xrplaccount-list')}"
    url += f"?{urlencode({'hash__contains': uuid4().hex})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 0
