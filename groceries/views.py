from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import GrocerySerializer, ItemSerializer, DailyIncomeSerializer
from .permissions import user_is_responsible_for_grocery
from .graph_nodes import GroceryNode, ItemNode, DailyIncomeNode

class GroceryListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        groceries = GroceryNode.nodes.all()
        data = [{"uid":g.uid,"name":g.name,"location":g.location,"created_at":g.created_at,"updated_at":g.updated_at} for g in groceries]
        return Response(data)

    def post(self, request):
        serializer = GrocerySerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        grocery = serializer.save()
        # return the serialized node (so response has uid, etc.)
        out = GrocerySerializer(grocery).data
        return Response(out, status=201)
    
class GroceryDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, grocery_uid):
        try:
            return GroceryNode.nodes.get(uid=grocery_uid)
        except GroceryNode.DoesNotExist:
            return None

    def get(self, request, grocery_uid):
        g = self.get_object(grocery_uid)
        if not g:
            return Response({"detail":"Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(GrocerySerializer(g).data)

    def patch(self, request, grocery_uid):
        if request.user.role != "ADMIN":
            return Response({"detail":"Only ADMIN can update groceries."}, status=status.HTTP_403_FORBIDDEN)
        g = self.get_object(grocery_uid)
        if not g:
            return Response({"detail":"Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = GrocerySerializer(g, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()
        return Response(GrocerySerializer(updated).data)

    def delete(self, request, grocery_uid):
        if request.user.role != "ADMIN":
            return Response({"detail":"Only ADMIN can delete groceries."}, status=status.HTTP_403_FORBIDDEN)
        g = self.get_object(grocery_uid)
        if not g:
            return Response({"detail":"Not found."}, status=status.HTTP_404_NOT_FOUND)
        g.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class GroceryItemsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_grocery(self, uid):
        try:
            return GroceryNode.nodes.get(uid=uid)
        except GroceryNode.DoesNotExist:
            return None

    def get(self, request, grocery_uid):
        grocery = self.get_grocery(grocery_uid)
        if not grocery:
            return Response({"detail":"Grocery not found."}, status=status.HTTP_404_NOT_FOUND)
        include_deleted = request.query_params.get("include_deleted") in ("1","true","True")
        items = [i for i in grocery.items.all() if (include_deleted or not i.is_deleted)]
        data = [ItemSerializer(i).data for i in items]
        return Response(data)

    def post(self, request, grocery_uid):
        grocery = self.get_grocery(grocery_uid)
        if not grocery:
            return Response({"detail":"Grocery not found."}, status=status.HTTP_404_NOT_FOUND)
        if request.user.role != "ADMIN" and not user_is_responsible_for_grocery(request.user.id, grocery_uid):
            return Response({"detail":"Not allowed to add items to this grocery."}, status=status.HTTP_403_FORBIDDEN)
        serializer = ItemSerializer(data=request.data, context={"grocery":grocery})
        serializer.is_valid(raise_exception=True)
        item = serializer.save()
        return Response(ItemSerializer(item).data, status=status.HTTP_201_CREATED)

class GroceryItemDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_grocery_and_item(self, grocery_uid, item_uid):
        try:
            grocery = GroceryNode.nodes.get(uid=grocery_uid)
        except GroceryNode.DoesNotExist:
            return None, None
        try:
            item = ItemNode.nodes.get(uid=item_uid)
        except ItemNode.DoesNotExist:
            return grocery, None
        if not grocery.items.is_connected(item):
            return grocery, None
        return grocery, item

    def patch(self, request, grocery_uid, item_uid):
        grocery, item = self.get_grocery_and_item(grocery_uid, item_uid)
        if not grocery or not item:
            return Response({"detail":"Not found."}, status=status.HTTP_404_NOT_FOUND)
        if request.user.role != "ADMIN" and not user_is_responsible_for_grocery(request.user.id, grocery_uid):
            return Response({"detail":"Not allowed."}, status=status.HTTP_403_FORBIDDEN)
        serializer = ItemSerializer(item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()
        return Response(ItemSerializer(updated).data)

    def delete(self, request, grocery_uid, item_uid):
        grocery, item = self.get_grocery_and_item(grocery_uid, item_uid)
        if not grocery or not item:
            return Response({"detail":"Not found."}, status=status.HTTP_404_NOT_FOUND)
        if request.user.role != "ADMIN" and not user_is_responsible_for_grocery(request.user.id, grocery_uid):
            return Response({"detail":"Not allowed."}, status=status.HTTP_403_FORBIDDEN)
        from datetime import datetime
        item.is_deleted = True
        item.deleted_at = datetime.utcnow()
        item.touch()
        return Response(status=status.HTTP_204_NO_CONTENT)

class GroceryIncomeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_grocery(self, uid):
        try:
            return GroceryNode.nodes.get(uid=uid)
        except GroceryNode.DoesNotExist:
            return None

    def get(self, request, grocery_uid):
        grocery = self.get_grocery(grocery_uid)
        if not grocery:
            return Response({"detail":"Grocery not found."}, status=status.HTTP_404_NOT_FOUND)
        mine = request.query_params.get("mine") in ("1","true","True")
        print("Runtime user_is_responsible_for_grocery(request.user.id, grocery_uid): ", user_is_responsible_for_grocery(request.user.id, grocery_uid))
        if request.user.role != "ADMIN":
            if not mine or not user_is_responsible_for_grocery(request.user.id, grocery_uid):
                return Response({"detail":"Only ADMIN can read incomes of other groceries."}, status=status.HTTP_403_FORBIDDEN)
        date_from = request.query_params.get("from")
        date_to = request.query_params.get("to")
        incomes = grocery.incomes.all()
        if date_from:
            incomes = [i for i in incomes if i.date >= date_from]
        if date_to:
            incomes = [i for i in incomes if i.date <= date_to]
        total = sum(i.amount for i in incomes)
        return Response({"grocery_uid":grocery.uid,"count":len(incomes),"total":total,"incomes":[DailyIncomeSerializer(i).data for i in incomes]})

    def post(self, request, grocery_uid):
        grocery = self.get_grocery(grocery_uid)
        if not grocery:
            return Response({"detail":"Grocery not found."}, status=status.HTTP_404_NOT_FOUND)
        if request.user.role != "ADMIN" and not user_is_responsible_for_grocery(request.user.id, grocery_uid):
            return Response({"detail":"Not allowed to add income to this grocery."}, status=status.HTTP_403_FORBIDDEN)
        serializer = DailyIncomeSerializer(data=request.data, context={"grocery":grocery})
        serializer.is_valid(raise_exception=True)
        income = serializer.save()
        return Response(DailyIncomeSerializer(income).data, status=status.HTTP_201_CREATED)
