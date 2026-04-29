import json
import os
from typing import List, Tuple
from datetime import datetime
from data_model import Transaction, BudgetRules, Category, CurrentState, AlertType

class FileHandler:
    TRANSACTIONS = "transactions.json"
    BUDGET_RULES = "budget_rules.json"

    @staticmethod
    def load_trans() -> Tuple[List[Transaction], List[str]]:
        errors = []
        try:
            if not os.path.isfile(FileHandler.TRANSACTIONS):
                return [], []
            
            with open(FileHandler.TRANSACTIONS, 'r') as f:
                content = f.read().strip()
                if not content:
                    return [], [] 
                
                data = json.loads(content)
                trans = []
                for index, i in enumerate(data):
                    try:
                        amt_flag = i["amount"] < 0
                        dsc_flag = i["description"] == ""
                        if amt_flag or dsc_flag:
                            if amt_flag:
                                errors.append(f"Transaction {index+1}: Amount is not a positive number")
                            if dsc_flag:
                                errors.append(f"Transaction {index+1}: Description is empty")
                        else:
                            trans.append(Transaction.fromDict(i))
                    except Exception as e:
                        errors.append(f"Transaction {index+1}: {str(e)}")
                        continue
                return trans, errors
        except json.JSONDecodeError as e:
            errors.append(f"Malformed transactions file: {str(e)}")
            return [], errors
        except Exception as e:
            errors.append(f"Error loading transactions: {str(e)}")
            return [], errors

    @staticmethod    
    def save_trans(trans: List[Transaction]) -> bool:
        try:
            data = [t.toDict() for t in trans]
            with open(FileHandler.TRANSACTIONS, 'w') as f:
                json.dump(data, f)
            return True
        except Exception:
            return False
        
    @staticmethod    
    def load_budget_rules() -> Tuple[List[BudgetRules], List[str]]:
        errors = []
        try:
            if not os.path.isfile(FileHandler.BUDGET_RULES):
                return [], []
            
            with open(FileHandler.BUDGET_RULES, 'r') as f:
                content = f.read().strip()
                if not content:
                    return [], []
                
                data = json.loads(content)
                budget = []
                for index, i in enumerate(data):
                    try:
                        period_str = ["Daily", "Weekly", "Monthly"]
                        thr_flag = i["threshold"] < 0
                        period_flag = i["period"] not in period_str
                        if thr_flag or period_flag:
                            if thr_flag:
                                errors.append(f"Transaction {index+1}: Threshold is not a positive number")
                            if period_flag:
                                errors.append(f"Transaction {index+1}: Period is not valid")
                        else:
                            budget.append(BudgetRules.fromDict(i))
                    except Exception as e:
                        errors.append(f"Budget rule {index+1}: {str(e)}")
                        continue
                return budget, errors
        except json.JSONDecodeError as e:
            errors.append(f"Malformed budget rules file: {str(e)}")
            return [], errors
        except Exception as e:
            errors.append(f"Error loading budget rules: {str(e)}")
            return [], errors

    @staticmethod    
    def save_budget_rules(rules: List[BudgetRules]) -> bool:
        try:
            data = [r.toDict() for r in rules]
            with open(FileHandler.BUDGET_RULES, 'w') as f:
                json.dump(data, f)
            return True
        except Exception:
            return False
          

    @staticmethod    
    def load_state() -> Tuple[CurrentState, List[str]]:
        trans, t_errors = FileHandler.load_trans()
        rules, r_errors = FileHandler.load_budget_rules()

        return CurrentState(
            transactions = trans,
            budget_rules = rules
        ), t_errors+r_errors
    
    

    @staticmethod
    def save_state(state: CurrentState) -> Tuple[bool, str]:
        trans_save = FileHandler.save_trans(state.transactions)
        budget_save = FileHandler.save_budget_rules(state.budget_rules)

        if trans_save and budget_save:
            return True, "Data saved succesfully"
        else:
            return False, "Error: data not saved"
        
    
    @staticmethod
    def delete_all(state: CurrentState):
        state.transactions.clear()
        state.budget_rules.clear()

        with open(FileHandler.TRANSACTIONS, 'w') as f:
            json.dump({}, f)

        with open(FileHandler.BUDGET_RULES, 'w') as f:
            json.dump({}, f)
