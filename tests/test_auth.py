import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_unauth_get_transactions(client, transaction):
    response = client.get(
        reverse("paymenttransaction-list"), HTTP_HOST="localhost:8001"
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_unauth_detail_transaction(client, transaction):
    response = client.get(
        reverse("paymenttransaction-detail", args=[transaction.pk]),
        HTTP_HOST="localhost:8001",
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_unauth_get_xrpl_accounts(client, transaction):
    response = client.get(reverse("xrplaccount-list"), HTTP_HOST="localhost:8001")
    assert response.status_code == 200


@pytest.mark.django_db
def test_unauth_get_assets(client, transaction):
    response = client.get(reverse("assetinfo-list"), HTTP_HOST="localhost:8001")
    assert response.status_code == 200
