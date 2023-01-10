import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_auth_get_transactions(auth_client, transaction):
    response = auth_client.get(reverse("list-create-payments"),
                               HTTP_HOST="localhost:8001")
    assert response.status_code == 200


@pytest.mark.django_db
def test_auth_retrieve_transaction(auth_client, transaction):
    response = auth_client.get(
        reverse("retrieve-update-delete-payments", args=[transaction.pk]),
        HTTP_HOST="localhost:8001",
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_auth_patch_transaction(auth_client, transaction):
    payload = {"ledger_idx": 125}
    response = auth_client.patch(
        reverse("retrieve-update-delete-payments", args=[transaction.pk]),
        data=payload, HTTP_HOST="localhost:8001", format="json",
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_auth_put_transaction(auth_client, transaction, payment_payload):
    response = auth_client.put(
        reverse("retrieve-update-delete-payments", args=[transaction.pk]),
        data=payment_payload,
        HTTP_HOST="localhost:8001",
        format="json",
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_auth_delete_transaction(auth_client, transaction):
    response = auth_client.delete(
        reverse("retrieve-update-delete-payments", args=[transaction.pk]),
        HTTP_HOST="localhost:8001",
        format="json",
    )
    assert response.status_code == 204


@pytest.mark.django_db
def test_unauth_get_transactions(client, transaction):
    response = client.get(reverse("list-create-payments"),
                          HTTP_HOST="localhost:8001")
    assert response.status_code == 200


@pytest.mark.django_db
def test_unauth_retrieve_transaction(client, transaction):
    response = client.get(
        reverse("retrieve-update-delete-payments", args=[transaction.pk]),
        HTTP_HOST="localhost:8001",
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_unauth_patch_transaction(client, transaction):
    payload = {"ledger_idx": 125}
    response = client.patch(
        reverse("retrieve-update-delete-payments", args=[transaction.pk]),
        data=payload, HTTP_HOST="localhost:8001", format="json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_unauth_put_transaction(client, transaction, payment_payload):
    response = client.put(
        reverse("retrieve-update-delete-payments", args=[transaction.pk]),
        data=payment_payload,
        HTTP_HOST="localhost:8001",
        format="json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_unauth_delete_transaction(client, transaction):
    response = client.delete(
        reverse("retrieve-update-delete-payments", args=[transaction.pk]),
        HTTP_HOST="localhost:8001",
        format="json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_get_invalid_auth(client_invalid_auth_token, transaction):
    response = client_invalid_auth_token.get(reverse("list-create-payments"),
                                             HTTP_HOST="localhost:8001")
    assert response.status_code == 401


@pytest.mark.django_db
def test_retrieve_invalid_auth(client_invalid_auth_token, transaction):
    response = client_invalid_auth_token.get(
        reverse("retrieve-update-delete-payments", args=[transaction.pk]),
        HTTP_HOST="localhost:8001",
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_patch_invalid_auth(client_invalid_auth_token, transaction):
    payload = {"ledger_idx": 125}
    response = client_invalid_auth_token.patch(
        reverse("retrieve-update-delete-payments", args=[transaction.pk]),
        data=payload, HTTP_HOST="localhost:8001", format="json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_put_invalid_auth(client_invalid_auth_token, transaction,
                          payment_payload):
    response = client_invalid_auth_token.put(
        reverse("retrieve-update-delete-payments", args=[transaction.pk]),
        data=payment_payload,
        HTTP_HOST="localhost:8001",
        format="json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_delete_invalid_auth(client_invalid_auth_token, transaction):
    response = client_invalid_auth_token.delete(
        reverse("retrieve-update-delete-payments", args=[transaction.pk]),
        HTTP_HOST="localhost:8001",
        format="json",
    )
    assert response.status_code == 401
