# expenses/urls.py
from django.urls import path
from .views import ExpenseListCreateView, ExpenseDetailView, InsightsView

urlpatterns = [
    path('expenses/', ExpenseListCreateView.as_view(), name='expense-list-create'),
    path('expenses/<int:pk>/', ExpenseDetailView.as_view(), name='expense-detail'),
    path('insights/', InsightsView.as_view(), name='insights'),
]