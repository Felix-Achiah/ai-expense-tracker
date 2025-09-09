# AI-Powered Expense Tracker API

This is a **Django-based RESTful API** for an expense tracking application with **AI-powered features**, including:

- Automatic expense categorization (Hugging Face Transformers)
- Personalized financial insights (monthly/weekly summaries, top categories, anomaly detection)

The project uses:
- **Django REST Framework** for API development
- **Hugging Face Transformers** for AI categorization
- **scikit-learn** for anomaly detection

---

## Prerequisites

- Python **3.8+**
- PostgreSQL **12+**
- `pip` and `virtualenv`
- Git (optional, for cloning the repository)

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd expense-tracker

2. Set Up the Environment

Create and activate a virtual environment:

python -m venv venv


Windows:

venv\Scripts\activate


macOS/Linux:

source venv/bin/activate


Install dependencies:

pip install -r requirements.txt


(Optional) Install hf_xet for faster Hugging Face model downloads:

pip install hf_xet

3. Configure Environment Variables

Create a .env file in the project root:

SECRET_KEY=your_secret_key_here
DB_NAME=expense_tracker
DB_USER=your_postgres_user
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432

# Optional
HF_HUB_DISABLE_SYMLINKS_WARNING=1  # Suppress Hugging Face symlink warning on Windows
HF_HOME=/path/to/model/cache        # Specify Hugging Face model cache directory


⚠️ Replace placeholders (your_secret_key_here, your_postgres_user, etc.) with your actual values.

Windows users may need to enable Developer Mode to support symlinks (see Hugging Face docs).

4. Set Up PostgreSQL Database

Ensure PostgreSQL is running, then create the database:

psql -U your_postgres_user -c "CREATE DATABASE expense_tracker;"

5. Run Database Migrations
python manage.py makemigrations
python manage.py migrate

6. Create a Superuser (Optional)
python manage.py createsuperuser


Follow the prompts to set username, email, and password.

7. Pre-Download AI Model (Optional, Recommended for Production)
python -c "from transformers import pipeline; pipeline('zero-shot-classification', model='facebook/bart-large-mnli')"


This will cache the facebook/bart-large-mnli model (~1.63GB).

8. Run the Development Server
python manage.py runserver


API: http://127.0.0.1:8000/api/

Swagger docs: http://127.0.0.1:8000/swagger/

Redoc docs: http://127.0.0.1:8000/redoc/

Authentication

All endpoints (except token and docs) require JWT authentication.

Obtain a Token
curl -X POST http://127.0.0.1:8000/api/token/ \
-H "Content-Type: application/json" \
-d '{"username": "your_username", "password": "your_password"}'

Use the Token
curl -X GET http://127.0.0.1:8000/api/expenses/ \
-H "Authorization: Bearer <your_access_token>"

Refresh Token
curl -X POST http://127.0.0.1:8000/api/token/refresh/ \
-H "Content-Type: application/json" \
-d '{"refresh": "your_refresh_token"}'

AI Features

Automatic Categorization
Uses Hugging Face’s facebook/bart-large-mnli model for zero-shot classification.
→ Example: “Bought coffee” → Food

Anomaly Detection
Uses IsolationForest to detect unusual spending patterns.

Production Optimization

Pre-download the model (Step 7) to avoid runtime delays

Use HF_HOME for centralized caching

For scalability, deploy via Hugging Face Inference API

Testing

Run the test suite:

python manage.py test


Tests include:

Unit tests for AI utilities (categorize_expense, detect_anomalies)

Integration tests for API endpoints (/expenses/, /insights/)

Deterministic results (fixed random seed)

API Usage Examples
Create an Expense
curl -X POST http://127.0.0.1:8000/api/expenses/ \
-H "Authorization: Bearer <your_access_token>" \
-H "Content-Type: application/json" \
-d '{
  "amount": 50.00,
  "description": "Bought coffee and snacks",
  "category": "",
  "date": "2025-09-09"
}'

List Expenses
curl -X GET http://127.0.0.1:8000/api/expenses/ \
-H "Authorization: Bearer <your_access_token>"

Get Insights
curl -X GET http://127.0.0.1:8000/api/insights/ \
-H "Authorization: Bearer <your_access_token>"

Notes

Modularity: AI logic lives in expenses/ai_utils.py → easy to swap models (e.g., LangChain).

Code Quality: PEP 8, DRF best practices, proper error handling.

Scalability: Efficient ORM queries + lightweight AI models.

Windows Users: For Hugging Face symlink warnings → enable Developer Mode or set HF_HUB_DISABLE_SYMLINKS_WARNING=1.

For issues or questions, check the Swagger docs:
👉 http://127.0.0.1:8000/swagger/