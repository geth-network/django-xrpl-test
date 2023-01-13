from urllib.parse import urlencode
from uuid import uuid4

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_get_payments_hash_exact_match(client, transaction, schema_tester):
    url = f"{reverse('paymenttransaction-list')}"
    url += f"?{urlencode({'hash': transaction.pk})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 1


@pytest.mark.django_db
def test_get_payments_hash_exact_empty(client, transaction, schema_tester):
    url = f"{reverse('paymenttransaction-list')}"
    url += f"?{urlencode({'hash': uuid4().hex})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 0


@pytest.mark.django_db
def test_get_payments_hash_contains_match(client, transaction, schema_tester):
    partial_hash = transaction.pk[:-1]
    url = f"{reverse('paymenttransaction-list')}"
    url += f"?{urlencode({'hash__contains': partial_hash})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 1


@pytest.mark.django_db
def test_get_payments_hash_contains_empty(client, transaction, schema_tester):
    url = f"{reverse('paymenttransaction-list')}"
    url += f"?{urlencode({'hash__contains': uuid4().hex})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 0


@pytest.mark.django_db
def test_get_payments_account_exact_match(client, transaction, schema_tester):
    url = f"{reverse('paymenttransaction-list')}"
    url += f"?{urlencode({'account': transaction.account_id})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 1


@pytest.mark.django_db
def test_get_payments_account_exact_empty(client, transaction, schema_tester):
    url = f"{reverse('paymenttransaction-list')}"
    url += f"?{urlencode({'account': uuid4().hex})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 0


@pytest.mark.django_db
def test_get_payments_account_contains_match(client, transaction,
                                             schema_tester):
    partial_id = transaction.account_id[:-1]
    url = f"{reverse('paymenttransaction-list')}"
    url += f"?{urlencode({'account__contains': partial_id})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 1


@pytest.mark.django_db
def test_get_payments_account_contains_empty(client, transaction,
                                             schema_tester):
    url = f"{reverse('paymenttransaction-list')}"
    url += f"?{urlencode({'account__contains': uuid4().hex})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 0


@pytest.mark.django_db
def test_get_payments_destination_exact_match(client, transaction,
                                              schema_tester):
    url = f"{reverse('paymenttransaction-list')}"
    url += f"?{urlencode({'destination': transaction.destination_id})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 1


@pytest.mark.django_db
def test_get_payments_destination_exact_empty(client, transaction,
                                              schema_tester):
    url = f"{reverse('paymenttransaction-list')}"
    url += f"?{urlencode({'destination': uuid4().hex})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 0


@pytest.mark.django_db
def test_get_payments_destination_contains_match(client, transaction,
                                                 schema_tester):
    partial_id = transaction.destination_id[:-1]
    url = reverse("paymenttransaction-list")
    url += f"?{urlencode({'destination__contains': partial_id})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 1


@pytest.mark.django_db
def test_get_payments_destination_contains_empty(client, transaction,
                                                 schema_tester):
    url = f"{reverse('paymenttransaction-list')}"
    url += f"?{urlencode({'destination__contains': uuid4().hex})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 0


@pytest.mark.django_db
def test_get_payments_issuer_exact_match(client, transaction, schema_tester):
    url = f"{reverse('paymenttransaction-list')}"
    url += f"?{urlencode({'issuer': transaction.asset_info.issuer_id})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 1


@pytest.mark.django_db
def test_get_payments_issuer_exact_empty(client, transaction, schema_tester):
    url = f"{reverse('paymenttransaction-list')}"
    url += f"?{urlencode({'issuer': uuid4().hex})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 0


@pytest.mark.django_db
def test_get_payments_issuer_contains_match(client, transaction,
                                            schema_tester):
    partial_id = transaction.asset_info.issuer_id[:-1]
    url = reverse("paymenttransaction-list")
    url += f"?{urlencode({'issuer__contains': partial_id})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 1


@pytest.mark.django_db
def test_get_payments_issuer_contains_empty(client, transaction,
                                            schema_tester):
    url = f"{reverse('paymenttransaction-list')}"
    url += f"?{urlencode({'issuer__contains': uuid4().hex})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 0


@pytest.mark.django_db
def test_get_payments_currency_exact_match(client, transaction, schema_tester):
    url = f"{reverse('paymenttransaction-list')}"
    url += f"?{urlencode({'currency': transaction.asset_info.currency})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 1


@pytest.mark.django_db
def test_get_payments_currency_exact_empty(client, transaction, schema_tester):
    url = f"{reverse('paymenttransaction-list')}"
    url += f"?{urlencode({'currency': uuid4().hex})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 0


@pytest.mark.django_db
def test_get_payments_currency_contains_match(client, transaction,
                                              schema_tester):
    partial_id = transaction.asset_info.currency[:-1]
    url = reverse("paymenttransaction-list")
    url += f"?{urlencode({'currency__contains': partial_id})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 1


@pytest.mark.django_db
def test_get_payments_currency_contains_empty(client, transaction,
                                              schema_tester):
    url = f"{reverse('paymenttransaction-list')}"
    url += f"?{urlencode({'currency__contains': uuid4().hex})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 0


@pytest.mark.django_db
def test_get_payments_destination_tag_exact_match(client, transaction,
                                                  schema_tester):
    url = f"{reverse('paymenttransaction-list')}"
    url += f"?{urlencode({'destination_tag': transaction.destination_tag})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 1


@pytest.mark.django_db
def test_get_payments_destination_tag_exact_empty(client, transaction,
                                                  schema_tester):
    url = f"{reverse('paymenttransaction-list')}"
    url += f"?{urlencode({'destination_tag': '100500'})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 0


@pytest.mark.django_db
def test_get_payments_destination_tag_isnull(client, transaction,
                                             schema_tester):
    url = reverse("paymenttransaction-list")
    url += f"?{urlencode({'destination_tag__isnull': True})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 1


@pytest.mark.django_db
def test_get_payments_destination_tag_isnotnull(client, transaction,
                                                schema_tester):
    url = f"{reverse('paymenttransaction-list')}"
    url += f"?{urlencode({'destination_tag__isnull': False})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 1


@pytest.mark.django_db
def test_get_payments_ledger_idx_exact_match(client, transaction,
                                             schema_tester):
    url = f"{reverse('paymenttransaction-list')}"
    url += f"?{urlencode({'ledger_idx': transaction.ledger_idx})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 1


@pytest.mark.django_db
def test_get_payments_ledger_idx_exact_empty(client, transaction,
                                             schema_tester):
    url = f"{reverse('paymenttransaction-list')}"
    url += f"?{urlencode({'ledger_idx': '100500'})}"
    response = client.get(url, HTTP_HOST="localhost:8001")
    schema_tester.validate_response(response)
    assert len(response.json()["results"]) == 0
