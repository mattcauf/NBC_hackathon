"""
Base Strategy Class
===================
Abstract base class that all strategies inherit from.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
from strategies.metrics import IncrementalMetrics


def round_qty_to_100(qty: int) -> int:
    """
    Round quantity down to nearest multiple of 100, clamped to [100, 500].
    
    Args:
        qty: Raw quantity value
        
    Returns:
        Quantity as a multiple of 100, between 100 and 500
    """
    rounded = (qty // 100) * 100
    return max(100, min(500, rounded))


class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.
    """
    
    def __init__(self, name: str):
        """
        Initialize strategy.
        
        Args:
            name: Strategy name for identification
        """
        self.name = name
    
    @abstractmethod
    def get_order(self, bid: float, ask: float, mid: float, inventory: int, 
                  step: int, metrics: IncrementalMetrics) -> Optional[Dict]:
        """
        Decide what order to submit (if any).
        
        Args:
            bid: Best bid price
            ask: Best ask price
            mid: Mid price
            inventory: Current position (positive = long, negative = short)
            step: Current simulation step
            metrics: IncrementalMetrics instance with current market metrics
            
        Returns:
            Order dict {"side": "BUY"|"SELL", "price": float, "qty": int} or None
        """
        pass
