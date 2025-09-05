import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

@pytest.mark.django_db
def test_auth_required():
    client = APIClient()
    resp = client.get("/api/groceries/")
    assert resp.status_code == 401

@pytest.mark.django_db
def test_admin_can_create_supplier_and_grocery():
    client = APIClient()
    admin = User.objects.create_user(username="admin", email="admin@example.com", name="Admin", password="pass", role="ADMIN")
    from rest_framework_simplejwt.tokens import RefreshToken
    token = str(RefreshToken.for_user(admin).access_token)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    resp = client.post("/api/accounts/suppliers/", {"name":"Supp","email":"s@example.com","password":"pass"})
    assert resp.status_code == 201
    supplier_id = resp.json()["id"]
    resp = client.post("/api/groceries/", {"name":"G1","location":"L1","responsible_supplier_id": supplier_id})
    assert resp.status_code == 201
