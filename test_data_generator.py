import random
from datetime import datetime, timedelta, date
import calendar
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

        transactions.sort(key=lambda t: t.date)  #sorting in ascending order
        rules = TestDataGenerator.generate_random_rules(income)

        return transactions, rules, income
    
    
    @staticmethod
    def generate_overspend_scenario():
        income = 5000
        transactions = []
        year, month = date.today().year, date.today().month
        days = calendar.monthrange(year, month)[1]
        day_list = sorted(date(year, month, random.randint(1, days)) for _ in range(5)) #sorting in ascending order

        for i in range(5):
            transactions.append(Transaction(
                date = day_list[i],
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
        """
        Loads JSON file with transactions and budget rules.
        Validates data using FileHandler validation logic.
        Ensures that if there are duplicate categories, only the largest amount in each category is subtracted from the remaining income.
        Returns (result, errors) where result is (transactions, rules, raw_income) or None if critical failure.
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            transactions = []
            rules = []
            raw_income = 0.0
            errors = []
            
            if isinstance(data, dict):
                # Extract income
                income_data = data.get("total_income", 0.0)
                if isinstance(income_data, dict):
                    raw_income = income_data.get("total", 0.0)
                else:
                    raw_income = income_data
                
                # Extract and validate transactions
                raw_trans = data.get("transactions", []) if isinstance(data, dict) else data
                for index, t in enumerate(raw_trans):
                    try:
                        # Validate data that does not automatically raise error
                        amt_flag = t.get("amount", 0) <= 0
                        dsc_flag = t.get("description", "") == ""
                        
                        if amt_flag or dsc_flag:
                            if amt_flag:
                                errors.append(f"Transaction {index+1}: Amount is not a positive number")
                            if dsc_flag:
                                errors.append(f"Transaction {index+1}: Description is empty")
                        else:
                            transactions.append(Transaction.fromDict(t))
                    except Exception as e:
                        errors.append(f"Transaction {index+1}: {str(e)}")
                        continue
                
                # Extract and validate budget rules
                raw_rules = data.get("budget_rules", []) if isinstance(data, dict) else []
                current = raw_income
                
                for index, r in enumerate(raw_rules):
                    try:
                        # Validate data that does not automatically raise error
                        period_str = ["Daily", "Weekly", "Monthly"]
                        thr_flag = r.get("threshold", 0) <= 0
                        period_flag = r.get("period", "") not in period_str
                        total_flag = r.get("threshold", 0) > current
                        
                        if thr_flag or period_flag or total_flag:
                            if thr_flag:
                                errors.append(f"Budget rule {index+1}: Threshold is not a positive number")
                            if period_flag:
                                errors.append(f"Budget rule {index+1}: Period is not valid")
                            if total_flag:
                                errors.append(f"Budget rule {index+1}: Threshold exceeds remaining income")
                        else:
                            subtract = 0
                            
                            # Ensures that if there are duplicate categories, only the largest amount in each category is subtracted from the remaining income
                            repeat_cat = [rule for rule in rules if rule.category == Category(r['category'])]
                            
                            if repeat_cat:
                                for match in repeat_cat:
                                    if r["threshold"] <= match.threshold:
                                        continue
                                    else:
                                        subtract += r["threshold"] - match.threshold
                            else:
                                subtract = r["threshold"]
                            
                            print(current)
                            current -= subtract
                            rules.append(BudgetRules.fromDict(r))
                    except Exception as e:
                        errors.append(f"Budget rule {index+1}: {str(e)}")
                        continue
                        
            elif isinstance(data, list):
                for item in data:
                    try:
                        transactions.append(Transaction.fromDict(item))
                    except:
                        try:
                            rules.append(BudgetRules.fromDict(item))
                        except:
                            continue
                
            return (transactions, rules, raw_income, current), errors
            
        except json.JSONDecodeError as e:
            return None, [f"Malformed JSON file: {str(e)}"]
        except Exception as e:
            return None, [f"File Error: {str(e)}"]
