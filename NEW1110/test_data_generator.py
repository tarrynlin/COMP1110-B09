import random
from datetime import datetime, timedelta
from data_model import Transaction, Category, BudgetRules, AlertType, CurrentState
import json
import os

class TestDataGenerator:
    @staticmethod
    def generate_sample_data(days=30):
        income = float(random.randrange(3000, 10000, 1000))
        transactions = []
        now = datetime.now()

        patterns = {
            Category.MEALS: {
                "price_range": (20, 100),
                "descriptions": ["Breakfast", "Lunch", "Dinner", "Dessert", "Coffee", "Snack"]},
            Category.TRANSPORT:  {
                "price_range": (2, 20),
                "descriptions": ["MTR", "Bus", "Uber"]},
            Category.SHOPPING: {
                "price_range": (50, 200),
                "descriptions": ["Fashion", "Cosmetics", "Groceries"]},
            Category.ENTERTAINMENT: {
                "price_range": (50, 200),
                "descriptions": ["Netflix", "Cinema", "Arcade"]},
            Category.UTILITIES: {
                "price_range": (300, 1000),
                "descriptions": ["Water Bill", "Electricity", "Internet", "Phone Plan"]},
            Category.OTHER: {
                "price_range": (10, 100),
                "descriptions": ["Gift", "Donation", "Miscellaneous"]},
            Category.UNCATEGORISED: {
                "price_range": (20, 100),
                "descriptions": ["Unnamed Transaction"]}
        }

        for d in range(days):
            base_date = now - timedelta(days = d)
            for cat, details in patterns.items():
                min_p, max_p = details["price_range"]
                descs = details["descriptions"]

                if cat == Category.MEALS:
                    chance = 0.40
                elif cat == Category.TRANSPORT:
                    chance = 0.30
                elif cat == Category.SHOPPING:
                    chance = 0.10
                elif cat == Category.ENTERTAINMENT:
                    chance = 0.065
                elif cat == Category.UTILITIES:
                    chance = 0.02
                elif cat == Category.OTHER:
                    chance = 0.05
                else:
                    chance = 0.065

                if random.random() <chance:
                    if cat in [Category.MEALS, Category.TRANSPORT]:
                        transaction_freq = random.randint(1, 3)
                    else:
                        transaction_freq = 1
                    for i in range(transaction_freq):
                        hour = random.randint(7, 22)
                        minute = random.randint(0, 59)
                        t_date = base_date.replace(hour = hour, minute = minute)

                        t = Transaction(
                            date = t_date,
                            category = cat,
                            description = random.choice(descs),
                            amount = round(random.uniform(min_p, max_p), 2)
                        )
                        transactions.append(t)
        rules = TestDataGenerator.generate_random_rules(income)

        return transactions, rules, income

    @staticmethod
    def generate_empty_scenario():
        return [], [], 0.0
    
    @staticmethod
    def generate_overspend_scenario():
        income = 5000
        transactions = []

        for i in range(5):
            transactions.append(Transaction(
                date = datetime.now(),
                category = Category.MEALS, 
                description = "Expensive Party Dinner",
                amount = 500.00
            ))
    
        rules = TestDataGenerator.generate_random_rules(income)
        return transactions, rules, income

    @staticmethod
    def generate_random_rules(total_income: float):
        rules = []
        plan = {
            Category.MEALS: 0.35,
            Category.TRANSPORT: 0.15,
            Category.SHOPPING: 0.20,
            Category.ENTERTAINMENT: 0.10,
            Category.OTHER: 0.10,
            Category.UTILITIES: 0.10
        }

        for cat, percentage in plan.items():
            threshold = total_income * percentage
            alert = random.choice([AlertType.WARNING, AlertType.CRITICAL])
            rules.append(BudgetRules(
                category = cat,
                period = "Monthly",
                threshold = round(threshold, 2),
                alert = alert
            ))
        return rules
    
    @staticmethod
    def load_json(file_path: str):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            transactions = []
            rules = []
            raw_income = 0.0
            if isinstance(data, dict):
                income_data = data.get("total_income", 0.0)
                if isinstance(income_data, dict):
                    raw_income = income_data.get("total", 0.0)
                else:
                    raw_income = income_data
                raw_trans = data.get("transactions", []) if isinstance(data, dict) else data
                raw_rules = data.get("budget_rules", []) if isinstance(data, dict) else []
                for t in raw_trans:
                    transactions.append(Transaction.fromDict(t))
                for r in raw_rules:
                    rules.append(BudgetRules.fromDict(r))
            elif isinstance(data, list):
                for item in data:
                    try:
                        transactions.append(Transaction.fromDict(item))
                    except:
                        try:
                            rules.append(BudgetRules.fromDict(item))
                        except:
                            continue
                
            return (transactions, rules, raw_income), "Success"
        except Exception as e:
            return None, f"File Error: {str(e)}"
