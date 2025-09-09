from rest_framework import serializers
from .models import Expense


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ['id', 'amount', 'description', 'category', 'date']

class InsightSerializer(serializers.Serializer):
    monthly_summary = serializers.DictField()
    weekly_summary = serializers.DictField()
    top_categories = serializers.ListField(child=serializers.DictField())
    anomalies = serializers.ListField(child=serializers.IntegerField())