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
    """
    Represents user's total income and the remaining income after total income has been allocated to budget rules
    """
    total : float
    current : float

    def toDict(self) -> dict:
        return {
            "total": self.total,
            "current": self.current
        }


@dataclass
class Transaction:
    """
    Represents a transaction 
    """
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
        date_raw = data["date"]
        if "T" in date_raw:
            date_obj = datetime.fromisoformat(date_raw)
        else:
            date_obj = datetime.strptime(date_raw, "%Y-%m-%d")
        return Transaction(
            date=date_obj,
            amount=float(data["amount"]),
            category=Category(data["category"]),
            description=data["description"]
        )
@dataclass    
class BudgetRules:
    """
    Represents a budget rule
    """
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
    total_income: TotalIncome 
    transactions: List[Transaction] = field(default_factory=list)
    budget_rules: List[BudgetRules] = field(default_factory=list)
