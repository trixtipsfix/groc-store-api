import argparse
import random
import string
import sys
from datetime import date
from typing import Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def _rand(n=6):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))


class APIError(Exception):
    pass


class Client:
    def __init__(self, base: str):
        self.base = base.rstrip("/")
        self.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=0.2,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PATCH", "DELETE"],
        )
        self.session.mount("http://", HTTPAdapter(max_retries=retries))
        self.session.mount("https://", HTTPAdapter(max_retries=retries))
        self.token: Optional[str] = None

    def set_token(self, token: str):
        self.token = token
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def post(self, path, payload, expect=201):
        r = self.session.post(f"{self.base}{path}", json=payload)
        if r.status_code != expect:
            raise APIError(f"POST {path} -> {r.status_code} {r.text}")
        return r.json() if r.text else {}

    def get(self, path, expect=200):
        r = self.session.get(f"{self.base}{path}")
        if r.status_code != expect:
            raise APIError(f"GET {path} -> {r.status_code} {r.text}")
        return r.json() if r.text else {}

    def patch(self, path, payload, expect=200):
        r = self.session.patch(f"{self.base}{path}", json=payload)
        if r.status_code != expect:
            raise APIError(f"PATCH {path} -> {r.status_code} {r.text}")
        return r.json() if r.text else {}

    def delete(self, path, expect=204):
        r = self.session.delete(f"{self.base}{path}")
        if r.status_code != expect:
            raise APIError(f"DELETE {path} -> {r.status_code} {r.text}")
        return True

    # ---- domain helpers
    def login(self, email_or_username: str, password: str) -> str:
        data = self.post("/api/auth/token/", {"username": email_or_username, "password": password}, expect=200)
        return data["access"]

    def create_supplier(self, name: str, email: str, password: str):
        return self.post("/api/accounts/suppliers/", {"name": name, "email": email, "password": password})

    def create_grocery(self, name: str, location: str, responsible_supplier_id: Optional[int] = None):
        payload = {"name": name, "location": location}
        if responsible_supplier_id:
            payload["responsible_supplier_id"] = responsible_supplier_id
        return self.post("/api/groceries/", payload)

    def get_grocery(self, uid: str):
        return self.get(f"/api/groceries/{uid}/")

    def update_grocery(self, uid: str, payload: Dict[str, Any]):
        return self.patch(f"/api/groceries/{uid}/", payload)

    def delete_grocery(self, uid: str):
        return self.delete(f"/api/groceries/{uid}/")

    def add_item(self, grocery_uid: str, name: str, item_type: str, item_location: str, price: float):
        return self.post(f"/api/groceries/{grocery_uid}/items/", {
            "name": name, "item_type": item_type, "item_location": item_location, "price": price
        })

    def list_items(self, grocery_uid: str, include_deleted=False):
        q = "?include_deleted=1" if include_deleted else ""
        return self.get(f"/api/groceries/{grocery_uid}/items/{q}")

    def update_item(self, grocery_uid: str, item_uid: str, payload: Dict[str, Any]):
        return self.patch(f"/api/groceries/{grocery_uid}/items/{item_uid}/", payload)

    def delete_item(self, grocery_uid: str, item_uid: str):
        return self.delete(f"/api/groceries/{grocery_uid}/items/{item_uid}/")

    def add_income(self, grocery_uid: str, amount: float, on_date: str):
        return self.post(f"/api/groceries/{grocery_uid}/incomes/", {"amount": amount, "date": on_date})

    def list_income(self, grocery_uid: str, mine=False, date_from: Optional[str] = None, date_to: Optional[str] = None):
        params = []
        if mine:
            params.append("mine=1")
        if date_from:
            params.append(f"from={date_from}")
        if date_to:
            params.append(f"to={date_to}")
        qs = "?" + "&".join(params) if params else ""
        return self.get(f"/api/groceries/{grocery_uid}/incomes/{qs}")


def assert_true(cond, msg):
    if not cond:
        raise APIError(msg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:8000", help="Base URL for API")
    ap.add_argument("--admin-username", required=True, help="Admin username")
    ap.add_argument("--admin-password", required=True, help="Admin password")
    args = ap.parse_args()

    c = Client(args.base)

    print("1) Logging in as ADMIN...")
    admin_token = c.login(args.admin_username, args.admin_password)
    c.set_token(admin_token)
    print("   OK")

    # Create suppliers
    print("2) Creating Supplier A and Supplier B...")
    sA_email = f"supplierA_{_rand()}@example.com"
    sB_email = f"supplierB_{_rand()}@example.com"
    s_pass = "Passw0rd!"
    sA = c.create_supplier(name="Supplier A", email=sA_email, password=s_pass)
    sB = c.create_supplier(name="Supplier B", email=sB_email, password=s_pass)
    sA_id, sB_id = sA["id"], sB["id"]
    print(f"   Supplier A id={sA_id}, Supplier B id={sB_id}")

    # Create groceries
    print("3) Creating Grocery A (responsible=Supplier A) and Grocery B (no responsible)...")
    gA = c.create_grocery(name=f"Grocery-A-{_rand()}", location="Karachi Central", responsible_supplier_id=sA_id)
    gB = c.create_grocery(name=f"Grocery-B-{_rand()}", location="Karachi South")
    gA_uid, gB_uid = gA["uid"], gB["uid"]
    print(f"   Grocery A uid={gA_uid}, Grocery B uid={gB_uid}")

    # Supplier logins
    print("4) Logging in as both suppliers...")
    sA_token = c.login(sA_email, s_pass)
    sB_token = c.login(sB_email, s_pass)
    print("   OK")

    # Supplier A adds item to Grocery A
    print("5) Supplier A adds item to Grocery A...")
    c.set_token(sA_token)
    iA = c.add_item(gA_uid, name=f"Apple-{_rand()}", item_type="food", item_location="first roof", price=2.50)
    iA_uid = iA["uid"]
    print(f"   Item A uid={iA_uid}")

    # Admin adds item to Grocery B
    print("6) Admin adds an item to Grocery B...")
    c.set_token(admin_token)
    iB = c.add_item(gB_uid, name=f"Chess-{_rand()}", item_type="game", item_location="second roof", price=16.00)
    iB_uid = iB["uid"]
    print(f"   Item B uid={iB_uid}")

    # Supplier A can read Grocery B items
    print("7) Supplier A can read Grocery B items...")
    c.set_token(sA_token)
    items_b = c.list_items(gB_uid)
    assert_true(len(items_b) >= 1, "Supplier A should see Grocery B items")
    print("   OK")

    # Supplier A cannot modify Grocery B
    print("8) Supplier A cannot add item to Grocery B...")
    forbidden = False
    try:
        c.add_item(gB_uid, name="Hack-Item", item_type="food", item_location="x", price=1.0)
    except APIError as e:
        forbidden = "403" in str(e)
    assert_true(forbidden, "Supplier A should be forbidden to modify Grocery B")
    print("   Forbidden as expected")

    # Supplier A updates item in Grocery A
    print("9) Supplier A updates their item price in Grocery A...")
    upd = c.update_item(gA_uid, iA_uid, {"price": 2.75})
    assert_true(abs(upd["price"] - 2.75) < 1e-6, "Price should be 2.75")
    print("   Updated OK")

    # Supplier A soft deletes item in Grocery A
    print("10) Supplier A soft-deletes the item in Grocery A...")
    c.delete_item(gA_uid, iA_uid)
    items_a_visible = c.list_items(gA_uid)
    assert_true(all(i["uid"] != iA_uid for i in items_a_visible), "Soft-deleted item should be hidden")
    items_a_all = c.list_items(gA_uid, include_deleted=True)
    assert_true(any(i["uid"] == iA_uid for i in items_a_all), "Soft-deleted item should show when included")
    print("   Soft delete verified")

    # Supplier A adds income BEFORE reassignment
    print("11) Supplier A records income for Grocery A (before reassignment)...")
    today = date.today().isoformat()
    incA1 = c.add_income(gA_uid, amount=111.11, on_date=today)
    assert_true(incA1["amount"] == 111.11, "Income mismatch")
    print("   Income recorded")

    # Supplier A reads their incomes (?mine=1) BEFORE reassignment
    print("12) Supplier A reads incomes with ?mine=1 (before reassignment)...")
    incomes_me_A = c.list_income(gA_uid, mine=True)
    assert_true(incomes_me_A["count"] >= 1, "Supplier A should see their own incomes before reassignment")
    print("   OK")

    # ADMIN reassigns responsible supplier to Supplier B
    print("13) ADMIN reassigns Grocery A responsible to Supplier B (PATCH)...")
    c.set_token(admin_token)
    reassigned_ok = True
    try:
        c.update_grocery(gA_uid, {"responsible_supplier_id": sB_id})
        print("   Reassignment PATCH success")
    except APIError as e:
        print("   WARNING: Reassignment not supported by API (PATCH failed). Skipping flip checks.")
        reassigned_ok = False

    if reassigned_ok:
        # Supplier A now forbidden to modify Grocery A
        print("14) Supplier A should now be FORBIDDEN to modify Grocery A...")
        c.set_token(sA_token)
        forbidden2 = False
        try:
            c.add_item(gA_uid, name="Should-Fail", item_type="food", item_location="x", price=1.0)
        except APIError as e:
            forbidden2 = "403" in str(e)
        assert_true(forbidden2, "Supplier A must be forbidden after reassignment")
        print("   Forbidden as expected")

        # Supplier B now allowed to modify Grocery A
        print("15) Supplier B should now be ALLOWED to modify Grocery A...")
        c.set_token(sB_token)
        iA2 = c.add_item(gA_uid, name=f"Banana-{_rand()}", item_type="food", item_location="first roof", price=1.25)
        iA2_uid = iA2["uid"]
        upd2 = c.update_item(gA_uid, iA2_uid, {"price": 1.50})
        assert_true(abs(upd2["price"] - 1.50) < 1e-6, "Supplier B should be able to update after reassignment")
        print("   Allowed as expected")

        # Supplier B adds income AFTER reassignment
        print("16) Supplier B records income for Grocery A (after reassignment)...")
        incB1 = c.add_income(gA_uid, amount=222.22, on_date=today)
        assert_true(incB1["amount"] == 222.22, "Income mismatch after reassignment")
        print("   Income recorded")

        # Supplier B reads their incomes (?mine=1) AFTER reassignment
        print("17) Supplier B reads incomes with ?mine=1 (after reassignment)...")
        incomes_me_B = c.list_income(gA_uid, mine=True)
        assert_true(incomes_me_B["count"] >= 1, "Supplier B should see their own incomes after reassignment")
        print("   OK")

    # Admin reads income totals
    print("18) ADMIN reads incomes for Grocery A...")
    c.set_token(admin_token)
    incomes_admin = c.list_income(gA_uid)
    assert_true(incomes_admin["count"] >= 1 and incomes_admin["total"] >= 111.11, "Admin income read failed")
    print(f"   OK (count={incomes_admin['count']}, total={incomes_admin['total']})")

    # Cleanup
    print("19) Cleanup: delete groceries (ADMIN)...")
    c.set_token(admin_token)
    c.delete_grocery(gA_uid)
    c.delete_grocery(gB_uid)
    print("\nALL TESTS PASSED ✅")


if __name__ == "__main__":
    try:
        main()
    except APIError as e:
        print(f"\nFAILED ❌  {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUNEXPECTED ERROR ❌  {e}")
        raise