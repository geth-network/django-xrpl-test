import pytest
from django.urls import reverse
from django.conf import settings


@pytest.mark.django_db
def test_get_transactions(client, transaction, schema_tester):
    response = client.get(reverse("list-create-payments"),
                          HTTP_HOST='localhost:8001')
    schema_tester.validate_response(response)


@pytest.mark.django_db
def test_create_transactions(auth_client, payment_payload, schema_tester):
    response = auth_client.post(reverse("list-create-payments"),
                                data=payment_payload,
                                HTTP_HOST='localhost:8001', format="json")
    schema_tester.validate_response(response)


@pytest.mark.xfail
@pytest.mark.django_db
def test_retrieve_transaction(auth_client, transaction, schema_tester):
    response = auth_client.get(
        reverse("retrieve-update-delete-payments", args=[transaction.pk]),
        HTTP_HOST='localhost:8001', format="json"
    )
    schema_tester.validate_response(response)


@pytest.mark.xfail
@pytest.mark.django_db
def test_patch_transaction(auth_client, transaction, schema_tester):
    payload = {"ledger_idx": 125}
    response = auth_client.patch(
        reverse("retrieve-update-delete-payments", args=[transaction.pk]),
        data=payload, HTTP_HOST='localhost:8001', format="json"
    )
    schema_tester.validate_response(response)


@pytest.mark.xfail
@pytest.mark.django_db
def test_put_transaction(auth_client, transaction, payment_payload,
                         schema_tester):
    response = auth_client.put(
        reverse("retrieve-update-delete-payments", args=[transaction.pk]),
        data=payment_payload, HTTP_HOST='localhost:8001', format="json"
    )
    schema_tester.validate_response(response)


@pytest.mark.xfail
@pytest.mark.django_db
def test_delete_transaction(auth_client, transaction, schema_tester):
    response = auth_client.delete(
        reverse("retrieve-update-delete-payments", args=[transaction.pk]),
        HTTP_HOST='localhost:8001', format="json"
    )
    schema_tester.validate_response(response)
