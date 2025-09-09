# expenses/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Expense
from .serializers import ExpenseSerializer, InsightSerializer
from .ai_utils import categorize_expense, detect_anomalies
from django.db.models import Sum
from django.db.models.functions import TruncMonth, TruncWeek
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import datetime


class ExpenseListCreateView(generics.ListCreateAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    @swagger_auto_schema(
        operation_description="Create a new expense. If category is empty, AI will predict it.",
        request_body=ExpenseSerializer,
        responses={201: ExpenseSerializer, 400: 'Bad Request'}
    )
    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        if not data.get('category'):
            description = data.get('description', '')
            data['category'] = categorize_expense(description)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ExpenseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    @swagger_auto_schema(
        operation_description="Update an expense. User can override category.",
        request_body=ExpenseSerializer,
        responses={200: ExpenseSerializer, 400: 'Bad Request', 404: 'Not Found'}
    )
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete an expense.",
        responses={204: 'No Content', 404: 'Not Found'}
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class InsightsView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = InsightSerializer

    @swagger_auto_schema(
        operation_description="Get personalized insights: summaries, top categories, anomalies.",
        responses={200: InsightSerializer}
    )
    def get(self, request, *args, **kwargs):
        expenses = Expense.objects.filter(user=request.user)
        if not expenses.exists():
            return Response({"detail": "No expenses found."}, status=status.HTTP_404_NOT_FOUND)

        # Monthly summary
        monthly = expenses.annotate(month=TruncMonth('date')).values('month').annotate(total=Sum('amount')).order_by('-month')

        # Weekly summary
        weekly = expenses.annotate(week=TruncWeek('date')).values('week').annotate(total=Sum('amount')).order_by('-week')

        # Top categories
        top_categories = expenses.values('category').annotate(total=Sum('amount')).order_by('-total')[:5]

        # Anomalies
        anomalies = detect_anomalies(list(expenses))

        data = {
            'monthly_summary': {str(m['month']): m['total'] for m in monthly},
            'weekly_summary': {str(w['week']): w['total'] for w in weekly},
            'top_categories': list(top_categories),
            'anomalies': anomalies
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)