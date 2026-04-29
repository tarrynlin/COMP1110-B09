import random
from datetime import datetime, timedelta
from data_model import Transaction, Category, BudgetRules, AlertType

class TestDataGenerator:
    @staticmethod
    def generate_sample_data(days=30):
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
            Category.UNCATEGORISED: {
                "price_range": (50, 200),
                "descriptions": ["Cash Withdrawal", "Top Up Other"]}
        }

        for d in range(days):
            base_date = now - timedelta(days = d)
            for cat, details in patterns.items():
                min_p, max_p = details["price_range"]
                descs = details["descriptions"]

                if cat == Category.MEALS:
                    chance = 0.5
                elif cat == Category.TRANSPORT:
                    chance = 0.4
                elif cat == Category.SHOPPING:
                    chance = 0.05
                elif cat == Category.ENTERTAINMENT:
                    chance = 0.015
                else:
                    chance = 0.035

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
        rules = TestDataGenerator.generate_random_rules(num_rules=5)
        return transactions, rules

    @staticmethod
    def generate_empty_scenario():
        return [], []
    
    @staticmethod
    def generate_overspend_scenario():
        transactions = []

        for i in range(5):
            transactions.append(Transaction(
                date = datetime.now(),
                category = Category.MEALS, 
                description = "Expensive Party Dinner",
                amount = 500.00
            ))
    
        rules = TestDataGenerator.generate_random_rules(num_rules=3)
        return transactions, rules

    @staticmethod
    def generate_random_rules(num_rules = 3):
        rules = []
        constraints = {
            Category.MEALS: (["monthly"], 2000, 4000, 100),
            Category.TRANSPORT: (["monthly"], 250, 400, 50),
            Category.SHOPPING: (["monthly"], 200, 1000, 50),
            Category.ENTERTAINMENT: (["monthly"], 150, 500, 50),
            Category.UNCATEGORISED: (["monthly"], 200, 500, 50)
        }

        selected_cat = random.sample(list(constraints.keys()), num_rules)

        for cat in selected_cat:
            timeframes, min_val, max_val, step = constraints[cat]
            time_frame = random.choice(timeframes)
            amount = random.randrange(min_val, max_val + step, step)

            alert = random.choice([AlertType.WARNING, AlertType.CRITICAL])
            rules.append(BudgetRules(
                category = cat,
                period = time_frame,
                threshold = float(amount),
                alert = alert
            ))
        return rules
