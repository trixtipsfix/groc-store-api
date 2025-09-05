from rest_framework import serializers
from .graph_nodes import GroceryNode, ItemNode, DailyIncomeNode, UserNode

class GrocerySerializer(serializers.Serializer):
    uid = serializers.CharField(read_only=True)          # ← include uid
    name = serializers.CharField()
    location = serializers.CharField()
    responsible_supplier_id = serializers.IntegerField(required=False, allow_null=True)

    def to_representation(self, obj):
        # Ensure stable API payload
        data = {
            "uid": obj.uid,
            "name": obj.name,
            "location": obj.location,
            "created_at": obj.created_at,
            "updated_at": obj.updated_at,
        }
        # include responsible supplier id if present (helpful for UI/tests)
        try:
            resp = list(obj.responsible.all())
            if resp:
                # our graph uses user_id (string) -> cast to int for convenience if possible
                rid = resp[0].user_id
                data["responsible_supplier_id"] = int(rid) if str(rid).isdigit() else rid
        except Exception:
            pass
        return data

    def create(self, validated_data):
        request = self.context.get("request")
        supplier_id = validated_data.pop("responsible_supplier_id", None)

        grocery = GroceryNode(**validated_data).save()

        # Link admin -> MANAGES (defensive read)
        if request and getattr(request, "user", None):
            admin_node = UserNode.nodes.filter(user_id=str(request.user.id)).first()
            if admin_node:
                admin_node.manages.connect(grocery)

        # Link responsible supplier if provided (defensive read)
        if supplier_id:
            supplier_node = UserNode.nodes.filter(user_id=str(supplier_id)).first()
            if not supplier_node:
                raise serializers.ValidationError("Supplier not found or duplicate user nodes exist; please repair.")
            supplier_node.responsible_for.connect(grocery)

        grocery.touch()
        return grocery

    def update(self, instance, validated_data):
        supplier_id = validated_data.pop("responsible_supplier_id", None)

        for k, v in validated_data.items():
            setattr(instance, k, v)

        # Reassign responsible supplier if provided (clear then connect)
        if supplier_id is not None:
            # disconnect all
            for u in list(instance.responsible.all()):
                u.responsible_for.disconnect(instance)
            if supplier_id:
                supplier_node = UserNode.nodes.filter(user_id=str(supplier_id)).first()
                if not supplier_node:
                    raise serializers.ValidationError("Supplier not found or duplicate user nodes exist; please repair.")
                supplier_node.responsible_for.connect(instance)

        instance.touch()
        return instance
    
class ItemSerializer(serializers.Serializer):
    uid = serializers.CharField(read_only=True)
    name = serializers.CharField()
    item_type = serializers.CharField()
    item_location = serializers.CharField()
    price = serializers.FloatField()
    is_deleted = serializers.BooleanField(read_only=True)
    deleted_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        grocery = self.context["grocery"]
        item = ItemNode(**validated_data).save()
        grocery.items.connect(item)
        return item

    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.touch()
        return instance

class DailyIncomeSerializer(serializers.Serializer):
    uid = serializers.CharField(read_only=True)
    amount = serializers.FloatField()
    date = serializers.DateField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if isinstance(instance.date, str):
            data["date"] = instance.date
        return data

    def create(self, validated_data):
        grocery = self.context["grocery"]
        date_str = validated_data["date"].isoformat() if hasattr(validated_data["date"], "isoformat") else str(validated_data["date"])
        income = DailyIncomeNode(amount=validated_data["amount"], date=date_str).save()
        grocery.incomes.connect(income)
        return income
