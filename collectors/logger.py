"""
Data Logger for Market Experimentation
========================================
Structured JSONL logging for market data collection and analysis.
"""

import json
import os
from datetime import datetime
from typing import Dict, Optional, List


class DataLogger:
    """
    Logs market data, state, and actions to JSONL format for analysis.
    
    Each line is a complete JSON object representing one simulation step.
    """
    
    def __init__(self, scenario: str, run_id: str, experiment_name: str = "default", mode: str = "passive"):
        """
        Initialize the data logger.
        
        Args:
            scenario: Scenario name (e.g., "normal_market", "flash_crash")
            run_id: Unique identifier for this run
            experiment_name: Name of the experiment/strategy being tested
            mode: Collection mode ("passive" or "active")
        """
        self.scenario = scenario
        self.run_id = run_id
        self.experiment_name = experiment_name
        self.mode = mode
        
        # Create data directory structure
        os.makedirs("data/raw", exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{scenario}_{experiment_name}_{mode}_{timestamp}.jsonl"
        self.filepath = os.path.join("data", "raw", filename)
        
        # Open file for writing
        self.file = open(self.filepath, 'w')
        print(f"[DataLogger] Logging to {self.filepath}")
    
    def log_step(self, 
                 step: int,
                 bid: float,
                 ask: float,
                 mid: float,
                 bids: List[Dict],
                 asks: List[Dict],
                 last_trade: float,
                 inventory: int,
                 cash_flow: float,
                 pnl: float,
                 orders_sent: int,
                 action: Optional[Dict] = None,
                 fill: Optional[Dict] = None):
        """
        Log a single simulation step.
        
        Args:
            step: Simulation step number
            bid: Best bid price
            ask: Best ask price
            mid: Mid price
            bids: Full bid side order book (list of {"price": float, "qty": int})
            asks: Full ask side order book (list of {"price": float, "qty": int})
            last_trade: Most recent trade price
            inventory: Current position
            cash_flow: Cumulative cash from trades
            pnl: Mark-to-market PnL
            orders_sent: Total orders sent so far
            action: Order submitted this step (None if none)
            fill: Fill received this step (None if none)
        """
        # Calculate spread
        spread = round(ask - bid, 4) if bid > 0 and ask > 0 else 0
        
        # Calculate book depth (sum of quantities)
        bid_depth = sum(b.get("qty", 0) for b in bids) if bids else 0
        ask_depth = sum(a.get("qty", 0) for a in asks) if asks else 0
        
        record = {
            "step": step,
            "timestamp": datetime.now().isoformat(),
            "experiment": self.experiment_name,
            "scenario": self.scenario,
            "run_id": self.run_id,
            "mode": self.mode,
            "market": {
                "bid": bid,
                "ask": ask,
                "mid": mid,
                "spread": spread,
                "last_trade": last_trade
            },
            "book": {
                "bids": bids[:10] if bids else [],  # Top 10 levels
                "asks": asks[:10] if asks else [],
                "bid_depth": bid_depth,
                "ask_depth": ask_depth
            },
            "state": {
                "inventory": inventory,
                "cash_flow": cash_flow,
                "pnl": pnl,
                "orders_sent": orders_sent
            },
            "action": action,
            "fill": fill
        }
        
        self.file.write(json.dumps(record) + "\n")
        self.file.flush()  # Ensure data is written immediately
    
    def close(self):
        """Close the log file."""
        self.file.close()
        print(f"[DataLogger] Closed {self.filepath}")
    
    def get_filepath(self) -> str:
        """Get the filepath of the log file."""
        return self.filepath

