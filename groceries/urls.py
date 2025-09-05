from django.urls import path
from .views import GroceryListCreateView, GroceryDetailView, GroceryItemsView, GroceryItemDetailView, GroceryIncomeView

urlpatterns = [
    path("groceries/", GroceryListCreateView.as_view(), name="groceries"),
    path("groceries/<str:grocery_uid>/", GroceryDetailView.as_view(), name="grocery_detail"),
    path("groceries/<str:grocery_uid>/items/", GroceryItemsView.as_view(), name="grocery_items"),
    path("groceries/<str:grocery_uid>/items/<str:item_uid>/", GroceryItemDetailView.as_view(), name="grocery_item_detail"),
    path("groceries/<str:grocery_uid>/incomes/", GroceryIncomeView.as_view(), name="grocery_income"),
]
