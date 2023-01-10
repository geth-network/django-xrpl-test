from uuid import uuid4
import pytest
from django.urls import reverse
from urllib.parse import urlencode


@pytest.mark.django_db
def test_get_transactions_hash_exact_match(client, transaction, schema_tester):
    url = f"{reverse('list-create-payments')}?{urlencode({'hash': transaction.pk})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 1


@pytest.mark.django_db
def test_get_transactions_hash_exact_not_match(client, transaction, schema_tester):
    url = f"{reverse('list-create-payments')}?{urlencode({'hash': uuid4().hex})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 0


@pytest.mark.django_db
def test_get_transactions_hash_contains_match(client, transaction, schema_tester):
    partial_hash = transaction.pk[:-1]
    url = f"{reverse('list-create-payments')}?{urlencode({'hash__contains': partial_hash})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 1


@pytest.mark.django_db
def test_get_transactions_hash_contains_not_match(client, transaction, schema_tester):
    url = f"{reverse('list-create-payments')}?{urlencode({'hash__contains': uuid4().hex})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 0


@pytest.mark.django_db
def test_get_transactions_account_exact_match(client, transaction, schema_tester):
    url = f"{reverse('list-create-payments')}?{urlencode({'account': transaction.account_id})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) >= 1


@pytest.mark.django_db
def test_get_transactions_account_exact_not_match(client, transaction, schema_tester):
    url = f"{reverse('list-create-payments')}?{urlencode({'account': uuid4().hex})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 0


@pytest.mark.django_db
def test_get_transactions_account_contains_match(client, transaction, schema_tester):
    partial_id = transaction.account_id[:-1]
    url = f"{reverse('list-create-payments')}?{urlencode({'account__contains': partial_id})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) >= 1


@pytest.mark.django_db
def test_get_transactions_account_contains_not_match(client, transaction, schema_tester):
    url = f"{reverse('list-create-payments')}?{urlencode({'account__contains': uuid4().hex})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 0