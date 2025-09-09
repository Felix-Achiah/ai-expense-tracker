from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Expense
from .ai_utils import categorize_expense, detect_anomalies
from datetime import date, timedelta
import random
from decimal import Decimal


# ----------------------------
# UNIT TESTS
# ----------------------------

class ExpenseModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_create_expense(self):
        expense = Expense.objects.create(
            user=self.user,
            amount=100.00,
            description='Test expense',
            category='Food',
            date=date.today()
        )
        self.assertEqual(expense.amount, 100.00)
        self.assertEqual(expense.category, 'Food')

    def test_negative_amount_not_allowed(self):
        with self.assertRaises(Exception):
            Expense.objects.create(
                user=self.user,
                amount=-50.00,
                description='Invalid negative expense',
                category='Food',
                date=date.today()
            )

    def test_blank_description(self):
        expense = Expense.objects.create(
            user=self.user,
            amount=20.00,
            description='',
            category='Misc',
            date=date.today()
        )
        self.assertEqual(expense.description, '')


class AITest(TestCase):
    def test_categorize_expense(self):
        category = categorize_expense("Bought groceries at the supermarket")
        self.assertIn(category, ["Food", "Shopping"])  # deterministic top prediction

    def test_detect_anomalies(self):
        user = User.objects.create_user(username='anomalyuser', password='testpass')
        expenses = [
            Expense.objects.create(user=user, amount=50, description='Normal', category='Food', date=date.today()),
            Expense.objects.create(user=user, amount=55, description='Normal', category='Food', date=date.today()),
            Expense.objects.create(user=user, amount=60, description='Normal', category='Food', date=date.today()),
            Expense.objects.create(user=user, amount=1000, description='Anomaly', category='Other', date=date.today()),
        ]
        anomalies = detect_anomalies(expenses)
        self.assertIn(expenses[-1].id, anomalies)

    def test_detect_anomalies_with_small_dataset(self):
        """Ensure it handles too few expenses gracefully."""
        user = User.objects.create_user(username='smallset', password='testpass')
        expenses = [Expense.objects.create(user=user, amount=10, description='Only one', category='Other', date=date.today())]
        anomalies = detect_anomalies(expenses)
        self.assertIsInstance(anomalies, list)


# ----------------------------
# INTEGRATION TESTS
# ----------------------------

class ExpenseAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='apiuser', password='apipass')
        self.client = APIClient()
        response = self.client.post(reverse('token_obtain_pair'), {'username': 'apiuser', 'password': 'apipass'})
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        random.seed(42)  # deterministic AI

    def test_create_expense(self):
        data = {
            'amount': 200.00,
            'description': 'Dinner out',
            'category': 'Food',
            'date': date.today().isoformat()
        }
        response = self.client.post('/api/expenses/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Expense.objects.count(), 1)

    def test_get_expenses(self):
        Expense.objects.create(user=self.user, amount=100, description='Test', category='Test', date=date.today())
        response = self.client.get('/api/expenses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_expense(self):
        expense = Expense.objects.create(user=self.user, amount=100, description='Test', category='Test', date=date.today())
        data = {'category': 'Updated'}
        response = self.client.patch(f'/api/expenses/{expense.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expense.refresh_from_db()
        self.assertEqual(expense.category, 'Updated')

    def test_delete_expense(self):
        expense = Expense.objects.create(user=self.user, amount=100, description='Test', category='Test', date=date.today())
        response = self.client.delete(f'/api/expenses/{expense.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Expense.objects.count(), 0)

    def test_insights(self):
        today = date.today()
        for i in range(10):
            Expense.objects.create(
                user=self.user,
                amount=Decimal(str(round(random.uniform(10, 100), 2))),
                description=f'Test {i}',
                category='Food' if i % 2 == 0 else 'Transport',
                date=today - timedelta(days=i)
            )
        Expense.objects.create(user=self.user, amount=1000, description='Anomaly', category='Other', date=today)
        response = self.client.get('/api/insights/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('monthly_summary', response.data)
        self.assertIn('anomalies', response.data)

    def test_ai_categorization_on_create(self):
        data = {
            'amount': 50.00,
            'description': 'Bought coffee and snacks',
            'category': '',  # Empty triggers AI
            'date': date.today().isoformat()
        }
        response = self.client.post('/api/expenses/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expense = Expense.objects.first()
        self.assertEqual(expense.category, 'Food')

    # --- Edge Cases / Negative Integration Tests ---
    def test_create_expense_without_authentication(self):
        client = APIClient()  # no auth
        data = {'amount': 20, 'description': 'No auth test', 'category': 'Misc', 'date': date.today().isoformat()}
        response = client.post('/api/expenses/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_expense_with_invalid_data(self):
        data = {
            'amount': -10.00,  # Invalid negative
            'description': 'Invalid expense',
            'category': 'Food',
            'date': date.today().isoformat()
        }
        response = self.client.post('/api/expenses/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
