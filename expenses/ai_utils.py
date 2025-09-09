from transformers import pipeline
from sklearn.ensemble import IsolationForest
import numpy as np
import torch
import random
import os

# Fix seeds for determinism
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
torch.cuda.manual_seed_all(SEED)
os.environ['PYTHONHASHSEED'] = str(SEED)

CATEGORIES = [
    "Food", "Transportation", "Housing", "Utilities", "Entertainment",
    "Health", "Education", "Shopping", "Travel", "Other"
]

# Lazy initialization of classifier
_classifier = None

def get_classifier():
    global _classifier
    if _classifier is None:
        _classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    return _classifier

def categorize_expense(description):
    """
    Use zero-shot classification to predict category.
    """
    classifier = get_classifier()
    result = classifier(description, candidate_labels=CATEGORIES)
    return result['labels'][0]  # Return top category

def detect_anomalies(expenses):
    """
    Detect anomalies using Isolation Forest.
    :param expenses: List of Expense objects
    :return: List of anomalous expense IDs
    """
    if len(expenses) < 2:
        return []
    
    amounts = np.array([[exp.amount] for exp in expenses])
    model = IsolationForest(contamination=0.1, random_state=SEED)
    preds = model.fit_predict(amounts)
    anomalous_indices = np.where(preds == -1)[0]
    return [expenses[i].id for i in anomalous_indices]