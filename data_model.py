from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List

class Category(Enum):
    MEALS = "Meals"
    TRANSPORT = "Transport"
    SHOPPING = "Shopping"
    UTILITIES = "Utilities"
    ENTERTAINMENT = "Entertainment"
    OTHER = "Other"
    UNCATEGORISED = "Uncategorised"

class AlertType(Enum):
    WARNING = "Warning"
    CRITICAL = "Critical"

@dataclass
class TotalIncome:
    total : float
    current : float

    def toDict(self) -> dict:
        return {
            "total": self.total,
            "current": self.current
        }

@dataclass
class Transaction:
    date : datetime
    amount : float
    category : Category
    description : str

    def toDict(self) -> dict:
        return {
            "date": self.date.isoformat(),
            "amount": self.amount,
            "category": self.category.value,
            "description": self.description 
        }

    @staticmethod
    def fromDict(data: dict) -> 'Transaction':
        return Transaction(
            date=datetime.fromisoformat(data["date"]),
            amount=float(data["amount"]),
            category=Category(data["category"]),
            description=data["description"]
        )
@dataclass    
class BudgetRules:
    threshold: float
    category: Category
    period: str #or make another class?
    alert: AlertType

    def toDict(self) -> dict:
        return {
            "threshold": self.threshold,
            "category": self.category.value,
            "period": self.period,
            "alert": self.alert.value
        }
    
    @staticmethod
    def fromDict(data: dict) -> 'BudgetRules':
        return BudgetRules(
            threshold=float(data["threshold"]),
            category=Category(data['category']),
            period=data['period'],
            alert=AlertType(data["alert"])
        )


@dataclass    
class CurrentState:
    transactions: List[Transaction] = field(default_factory=list)
    budget_rules: List[BudgetRules] = field(default_factory=list)
