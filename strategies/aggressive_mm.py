"""
Aggressive Market Maker Strategy
=================================
Crosses the spread to guarantee fills for high activity.
"""

from typing import Dict, Optional
from strategies.base import BaseStrategy
from strategies.metrics import IncrementalMetrics


class AggressiveMarketMaker(BaseStrategy):
    """
    Aggressive market making strategy.
    
    Crosses the spread to guarantee fills, trades frequently for high notional.
    """
    
    def __init__(self, max_inventory: int = 3500, qty: int = 200, trade_freq: int = 10):
        """
        Initialize aggressive market maker.
        
        Args:
            max_inventory: Maximum inventory before stopping new positions
            qty: Order quantity
            trade_freq: Trade every N steps
        """
        super().__init__("aggressive_mm")
        self.max_inventory = max_inventory
        self.qty = qty
        self.trade_freq = trade_freq
    
    def get_order(self, bid: float, ask: float, mid: float, inventory: int,
                  step: int, metrics: IncrementalMetrics) -> Optional[Dict]:
        """
        Generate order based on aggressive market making logic.
        """
        # Force unwind if over limit
        if inventory >= self.max_inventory:
            return {"side": "SELL", "price": round(bid, 2), "qty": 300}
        if inventory <= -self.max_inventory:
            return {"side": "BUY", "price": round(ask, 2), "qty": 300}
        
        # Trade at specified frequency
        if step % self.trade_freq != 0:
            return None
        
        tick = 0.1

        spread = ask - bid

        # Tight quoting: try to be at the inside (or 1 tick inside if spread allows).
        improve = tick if spread >= 2 * tick else 0.0
        buy_base = bid + improve
        sell_base = ask - improve

        # Much smaller skew; cannot push quotes through the spread
        skew = -0.0002 * inventory
        skew = max(-0.2, min(0.2, skew))
        
        # Bias toward reducing position
        if inventory > 1000:
            raw = sell_base + skew
            price = min(ask, max(bid + tick, raw))
            return {"side": "SELL", "price": round(price, 1), "qty": self.qty}
        elif inventory < -1000:
            raw = buy_base + skew
            price = max(bid, min(ask - tick, raw))
            price = max(tick, price)
            return {"side": "BUY", "price": round(price, 1), "qty": self.qty}
        else:
            # Alternate sides
            if (step // self.trade_freq) % 2 == 0:
                raw = buy_base + skew
                price = max(bid, min(ask - tick, raw))
                price = max(tick, price)
                return {"side": "BUY", "price": round(price, 1), "qty": self.qty}
            else:
                raw = sell_base + skew
                price = min(ask, max(bid + tick, raw))
                return {"side": "SELL", "price": round(price, 1), "qty": self.qty}
