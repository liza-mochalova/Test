from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Callable, Any, List
from dataclasses import dataclass
from exceptions import BusinessRuleException
from schemas import OrderStatus, Priority

class OrderEvent(str, Enum):
    START = "start"       
    COMPLETE = "complete"    
    FAIL = "fail"             
    CANCEL = "cancel"     

@dataclass
class Transition:
    trigger: str
    source: str
    dest: str 

class OrderStateMachine:
    TRANSITIONS = [
        Transition('start', 'pending', 'in_progress'),
        Transition('cancel', 'pending', 'cancelled'),
        Transition('complete', 'in_progress', 'completed'),
        Transition('fail', 'in_progress', 'failed'),
    ]

    def __init__(self, order):
        self.order = order
        self.current = order.status
    
    def can(self, trigger: str) -> bool:
        for i in self.TRANSITIONS:
            if i.source == self.current and i.trigger == trigger:
                return True
        return False
    
    def execute(self, trigger: str) -> bool:
        transition = None
        for i in self.TRANSITIONS:
            if i.source == self.current and i.trigger == trigger:
                transition = i
                break
        if not transition:
            raise BusinessRuleException
        old_state = self.current
        self.current = transition.dest
        self.order.status = self.current
        return True
    

