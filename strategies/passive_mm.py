"""
Passive Market Maker Strategy
=============================
Provides liquidity by quoting both sides of the market.
"""

from typing import Dict, Optional
from strategies.base import BaseStrategy
from strategies.metrics import IncrementalMetrics


class PassiveMarketMaker(BaseStrategy):
    """
    Passive market making strategy.
    
    Quotes at mid price with inventory skew to maintain balanced position.
    """
    
    def __init__(self, skew_factor: float = 0.0002, max_inventory: int = 3000,
                 qty: int = 200, trade_freq: int = 15):
        """
        Initialize passive market maker.
        
        Args:
            skew_factor: How much to adjust quotes per unit of inventory
            max_inventory: Maximum inventory before stopping new positions
            qty: Order quantity
            trade_freq: Trade every N steps
        """
        super().__init__("passive_mm")
        self.skew_factor = skew_factor
        self.max_inventory = max_inventory
        self.qty = qty
        self.trade_freq = trade_freq
    
    def get_order(self, bid: float, ask: float, mid: float, inventory: int,
                  step: int, metrics: IncrementalMetrics) -> Optional[Dict]:
        """
        Generate order based on passive market making logic.
        """
        # Trade only at specified frequency
        if step % self.trade_freq != 0:
            return None
        
        # Don't exceed inventory limits
        if abs(inventory) >= self.max_inventory:
            return None
        
        spread = ask - bid
        tick = 0.1

        # If there's room, improve inside by 1 tick; otherwise join best bid/ask.
        improve = tick if spread >= 2 * tick else 0.0
        buy_base = bid + improve
        sell_base = ask - improve

        # Keep skew small (cents) and bounded so it cannot force crossing.
        skew = -self.skew_factor * inventory
        skew = max(-0.2, min(0.2, skew))

        if (step // self.trade_freq) % 2 == 0:
            # BUY: join/improve bid, never cross ask
            raw = buy_base + skew
            price = max(bid, min(ask - tick, raw))
            price = max(tick, price)
            return {"side": "BUY", "price": round(price, 1), "qty": self.qty}
        else:
            # SELL: join/improve ask, never cross bid
            raw = sell_base + skew
            price = min(ask, max(bid + tick, raw))
            return {"side": "SELL", "price": round(price, 1), "qty": self.qty}
