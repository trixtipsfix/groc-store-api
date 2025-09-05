from neomodel import StructuredNode, StringProperty, FloatProperty, UniqueIdProperty, DateTimeProperty, BooleanProperty, RelationshipTo, RelationshipFrom
from datetime import datetime
import uuid

def _uuid():
    return uuid.uuid4().hex  # 32-char hex, no dashes

class BaseNode(StructuredNode):
    uid = StringProperty(unique_index=True, default=_uuid)  # ← important
    created_at = FloatProperty()
    updated_at = FloatProperty()

    def touch(self):
        import time
        self.updated_at = time.time()
        if not self.created_at:
            self.created_at = self.updated_at
        self.save()

class UserNode(BaseNode):
    user_id = StringProperty(required=True, unique_index=True)
    name = StringProperty(required=True)
    email = StringProperty(required=True)
    # ❌ old (bad): choices={"ADMIN","SUPPLIER"}
    # ✅ new (good):
    role = StringProperty(
        required=True,
        choices={"ADMIN": "Admin", "SUPPLIER": "Supplier"}
        # or: choices=[("ADMIN", "Admin"), ("SUPPLIER", "Supplier")]
    )
    manages = RelationshipTo("GroceryNode", "MANAGES")
    responsible_for = RelationshipTo("GroceryNode", "RESPONSIBLE_FOR")

class GroceryNode(BaseNode):
    name = StringProperty(required=True, index=True)
    location = StringProperty(required=True)
    items = RelationshipTo("ItemNode","HAS_ITEM")
    incomes = RelationshipTo("DailyIncomeNode","RECORDED")
    managed_by = RelationshipFrom("UserNode","MANAGES")
    responsible = RelationshipFrom("UserNode","RESPONSIBLE_FOR")

class ItemNode(BaseNode):
    name = StringProperty(required=True)
    item_type = StringProperty(required=True)
    item_location = StringProperty(required=True)
    price = FloatProperty(required=True)
    is_deleted = BooleanProperty(default=False)
    deleted_at = DateTimeProperty(default=None)

class DailyIncomeNode(BaseNode):
    amount = FloatProperty(required=True)
    date = StringProperty(required=True)  # YYYY-MM-DD
