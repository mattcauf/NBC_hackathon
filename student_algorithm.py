"""
Student Trading Algorithm Template
===================================
Connect to the exchange simulator, receive market data, and submit orders.

    python student_algorithm.py --host ip:host --scenario normal_market --name your_name --password your_password --secure

YOUR TASK:
    Modify the `decide_order()` method to implement your trading strategy.
"""

import json
import websocket
import threading
import argparse
import time
import requests
import ssl
import urllib3
from typing import Dict, Optional

# Suppress SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Import strategy router
from strategies.router import StrategyRouter

# Import data logger
from collectors.logger import DataLogger


class TradingBot:
    """
    A trading bot that connects to the exchange simulator.
    
    Students should modify the `decide_order()` method to implement their strategy.
    """
    
    def __init__(self, student_id: str, host: str, scenario: str, password: str = None, secure: bool = False):
        self.student_id = student_id
        self.host = host
        self.scenario = scenario
        self.password = password
        self.secure = secure
        
        # Protocol configuration
        self.http_proto = "https" if secure else "http"
        self.ws_proto = "wss" if secure else "ws"
        
        # Session info (set after registration)
        self.token = None
        self.run_id = None
        
        # Trading state - track your position
        self.inventory = 0      # Current position (positive = long, negative = short)
        self.cash_flow = 0.0    # Cumulative cash from trades (negative when buying)
        self.pnl = 0.0          # Mark-to-market PnL (cash_flow + inventory * mid_price)
        self.current_step = 0   # Current simulation step
        self.orders_sent = 0    # Number of orders sent
        
        # Market data
        self.last_bid = 0.0
        self.last_ask = 0.0
        self.last_mid = 0.0
        
        # Store full order book data
        self.last_bids = []
        self.last_asks = []
        
        # Strategy router
        self.router = StrategyRouter()
        
        # WebSocket connections
        self.market_ws = None
        self.order_ws = None
        self.running = True
        
        # Latency measurement
        self.last_done_time = None          # When we sent DONE
        self.step_latencies = []            # Time between DONE and next market data
        self.order_send_times = {}          # order_id -> time sent
        self.fill_latencies = []            # Time between order and fill
        
        # Open order tracking (for cancel-opposite-side logic)
        self.open_buy_orders = {}           # order_id -> {"price": X, "qty": N, "step": S}
        self.open_sell_orders = {}          # order_id -> {"price": X, "qty": N, "step": S}
        
        # Order limits
        self.MAX_OPEN_ORDERS = 40           # Stay well under the 50 limit
        
        # Current regime (for regime-aware order management)
        self.current_regime = "CALIBRATING"
        
        # Data logger (initialized after registration)
        self.logger = None
        self.pending_fill = None            # Track fill for next log entry
    
    # =========================================================================
    # REGISTRATION - Get a token to start trading
    # =========================================================================
    
    def register(self) -> bool:
        """Register with the server and get an auth token."""
        print(f"[{self.student_id}] Registering for scenario '{self.scenario}'...")
        try:
            url = f"{self.http_proto}://{self.host}/api/replays/{self.scenario}/start"
            headers = {"Authorization": f"Bearer {self.student_id}"}
            if self.password:
                headers["X-Team-Password"] = self.password
            resp = requests.get(
                url,
                headers=headers,
                timeout=10,
                verify=not self.secure  # Disable SSL verification for self-signed certs
            )
            
            if resp.status_code != 200:
                print(f"[{self.student_id}] Registration FAILED: {resp.text}")
                return False
            
            data = resp.json()
            self.token = data.get("token")
            self.run_id = data.get("run_id")
            
            if not self.token or not self.run_id:
                print(f"[{self.student_id}] Missing token or run_id")
                return False
            
            print(f"[{self.student_id}] Registered! Run ID: {self.run_id}")
            
            # Initialize data logger
            self.logger = DataLogger(
                scenario=self.scenario,
                run_id=self.run_id,
                experiment_name="strategy_router",
                mode="active"
            )
            
            return True
            
        except Exception as e:
            print(f"[{self.student_id}] Registration error: {e}")
            return False
    
    # =========================================================================
    # CONNECTION - Connect to WebSocket streams
    # =========================================================================
    
    def connect(self) -> bool:
        """Connect to market data and order entry WebSockets."""
        try:
            # SSL options for self-signed certificates
            sslopt = {"cert_reqs": ssl.CERT_NONE} if self.secure else None
            
            # Market Data WebSocket
            market_url = f"{self.ws_proto}://{self.host}/api/ws/market?run_id={self.run_id}"
            self.market_ws = websocket.WebSocketApp(
                market_url,
                on_message=self._on_market_data,
                on_error=self._on_error,
                on_close=self._on_close,
                on_open=lambda ws: print(f"[{self.student_id}] Market data connected")
            )
            
            # Order Entry WebSocket
            order_url = f"{self.ws_proto}://{self.host}/api/ws/orders?token={self.token}&run_id={self.run_id}"
            self.order_ws = websocket.WebSocketApp(
                order_url,
                on_message=self._on_order_response,
                on_error=self._on_error,
                on_close=self._on_close,
                on_open=lambda ws: print(f"[{self.student_id}] Order entry connected")
            )
            
            # Start WebSocket threads
            threading.Thread(
                target=lambda: self.market_ws.run_forever(sslopt=sslopt),
                daemon=True
            ).start()
            
            threading.Thread(
                target=lambda: self.order_ws.run_forever(sslopt=sslopt),
                daemon=True
            ).start()
            
            # Wait for connections
            time.sleep(1)
            return True
            
        except Exception as e:
            print(f"[{self.student_id}] Connection error: {e}")
            return False
    
    # =========================================================================
    # MARKET DATA HANDLER - Called when new market data arrives
    # =========================================================================
    
    def _on_market_data(self, ws, message: str):
        """Handle incoming market data snapshot."""
        try:
            recv_time = time.time()
            data = json.loads(message)
            
            # Skip connection confirmation messages
            if data.get("type") == "CONNECTED":
                return
            
            # Measure step latency (time since we sent DONE)
            if self.last_done_time is not None:
                step_latency = (recv_time - self.last_done_time) * 1000  # ms
                self.step_latencies.append(step_latency)
            
            # Extract market data
            self.current_step = data.get("step", 0)
            self.last_bid = data.get("bid", 0.0)
            self.last_ask = data.get("ask", 0.0)
            
            # Capture full order book if available
            if data.get("type") in ["MARKET_DATA", "SNAPSHOT"] or "bids" in data:
                self.last_bids = data.get("bids", [])
                self.last_asks = data.get("asks", [])
            else:
                # If full book not available, create minimal book from best bid/ask
                self.last_bids = [{"price": self.last_bid, "qty": 0}] if self.last_bid > 0 else []
                self.last_asks = [{"price": self.last_ask, "qty": 0}] if self.last_ask > 0 else []
            
            # Log progress every 500 steps with latency stats
            if self.current_step % 500 == 0 and self.step_latencies:
                print(f"[{self.student_id}] Step {self.current_step} | bid: {self.last_bid} | ask: {self.last_ask} | mid: {self.last_mid}")
                avg_lat = sum(self.step_latencies[-100:]) / min(len(self.step_latencies), 100)
                print(f"[{self.student_id}] Step {self.current_step} | Orders: {self.orders_sent} | Inv: {self.inventory} | Avg Latency: {avg_lat:.1f}ms")
            
            # Calculate mid price
            if self.last_bid > 0 and self.last_ask > 0:
                self.last_mid = (self.last_bid + self.last_ask) / 2
            elif self.last_bid > 0:
                self.last_mid = self.last_bid
            elif self.last_ask > 0:
                self.last_mid = self.last_ask
            else:
                self.last_mid = 0
            
            # =============================================
            # ORDER MANAGEMENT: Prevent hitting 50 order limit
            # =============================================
            open_count = self._get_open_order_count()
            
            # Safety check: If at max open orders, cancel oldest to make room
            if open_count >= self.MAX_OPEN_ORDERS:
                self._cancel_old_orders(min(5, open_count))
                # Signal DONE and skip this step (don't send new order)
                self._send_done()
                return
            
            # =============================================
            # YOUR STRATEGY LOGIC GOES HERE
            # =============================================
            result = self.decide_order(self.last_bid, self.last_ask, self.last_mid)
            order = result["order"]
            self.current_regime = result["regime"]
            
            # Periodic cleanup: Cancel stale orders with regime-aware timeout
            # HFT markets move fast - cancel stale orders more aggressively
            stale_timeout = 30 if self.current_regime == "HFT" else 200
            if self.current_step % 50 == 0 and open_count > 0:
                self._cancel_stale_orders(max_age=stale_timeout)
            
            # Log this step
            if self.logger:
                self.logger.log_step(
                    step=self.current_step,
                    bid=self.last_bid,
                    ask=self.last_ask,
                    mid=self.last_mid,
                    bids=self.last_bids,
                    asks=self.last_asks,
                    last_trade=0.0,  # Not tracked in base TradingBot
                    inventory=self.inventory,
                    cash_flow=self.cash_flow,
                    pnl=self.pnl,
                    orders_sent=self.orders_sent,
                    action=order,
                    fill=self.pending_fill
                )
                self.pending_fill = None
            
            if order and self.order_ws and self.order_ws.sock:
                # Cancel opposite orders that would cause self-match
                self._cancel_conflicting_orders(order["side"], order["price"])
                self._send_order(order)
            
            # Signal DONE to advance to next step
            self._send_done()
            
        except Exception as e:
            print(f"[{self.student_id}] Market data error: {e}")
    
    # =========================================================================
    # YOUR STRATEGY - MODIFY THIS METHOD!
    # =========================================================================
    
    def decide_order(self, bid: float, ask: float, mid: float) -> Dict:
        """
        ╔══════════════════════════════════════════════════════════════════╗
        ║                    YOUR STRATEGY GOES HERE!                       ║
        ╠══════════════════════════════════════════════════════════════════╣
        ║  Input:                                                           ║
        ║    - bid: Best bid price                                          ║
        ║    - ask: Best ask price                                          ║
        ║    - mid: Mid price (average of bid and ask)                      ║
        ║                                                                   ║
        ║  Available state:                                                 ║
        ║    - self.inventory: Your current position                         ║
        ║    - self.pnl: Your realized PnL                                  ║
        ║    - self.current_step: Current simulation step                   ║
        ║                                                                   ║
        ║  Return:                                                          ║
        ║    - {"side": "BUY"|"SELL", "price": X, "qty": N}                 ║
        ║    - Or return None to not send an order                          ║
        ╚══════════════════════════════════════════════════════════════════╝
        """
        
        # Skip if no valid prices
        if mid <= 0 or bid <= 0 or ask <= 0:
            return {"order": None, "regime": self.current_regime}
        
        # Calculate book depth
        bid_depth = sum(b.get("qty", 0) for b in self.last_bids) if self.last_bids else 1000
        ask_depth = sum(a.get("qty", 0) for a in self.last_asks) if self.last_asks else 1000
        
        # Delegate to strategy router
        return self.router.decide_order(
            bid=bid,
            ask=ask,
            mid=mid,
            inventory=self.inventory,
            step=self.current_step,
            bid_depth=bid_depth,
            ask_depth=ask_depth
        )
    
    # =========================================================================
    # ORDER HANDLING
    # =========================================================================
    
    def _cancel_order(self, order_id: str):
        """Cancel an order by ID."""
        msg = {
            "action": "CANCEL",
            "order_id": order_id
        }
        try:
            self.order_ws.send(json.dumps(msg))
        except Exception as e:
            print(f"[{self.student_id}] Cancel order error: {e}")

    def _cancel_order_ids(self, order_ids):
        """Cancel a list of order IDs and remove them from local tracking."""
        for order_id in order_ids:
            self._cancel_order(order_id)
            self.open_buy_orders.pop(order_id, None)
            self.open_sell_orders.pop(order_id, None)

    def _cancel_same_side_orders(self, side: str):
        """Cancel any existing open orders on the same side (replace semantics)."""
        if side == "BUY":
            self._cancel_order_ids(list(self.open_buy_orders.keys()))
        else:
            self._cancel_order_ids(list(self.open_sell_orders.keys()))

    def _cancel_conflicting_orders(self, new_side: str, new_price: float):
        """
        Cancel opposite-side orders ONLY if the new order would cross them.
        This prevents self-match without destroying two-sided quoting.
        """
        if new_side == "BUY":
            # Buying at/above an existing sell would cross our own sell
            to_cancel = [
                oid for oid, meta in self.open_sell_orders.items()
                if meta.get("price", float("inf")) <= new_price
            ]
            self._cancel_order_ids(to_cancel)
        else:
            # Selling at/below an existing buy would cross our own buy
            to_cancel = [
                oid for oid, meta in self.open_buy_orders.items()
                if meta.get("price", float("-inf")) >= new_price
            ]
            self._cancel_order_ids(to_cancel)

    def _get_open_order_count(self) -> int:
        """Return total number of open orders."""
        return len(self.open_buy_orders) + len(self.open_sell_orders)

    def _cancel_old_orders(self, count: int):
        """Cancel the oldest N orders (by step they were submitted)."""
        # Gather all orders with their step
        all_orders = []
        for oid, meta in self.open_buy_orders.items():
            all_orders.append((oid, meta.get("step", 0), "BUY"))
        for oid, meta in self.open_sell_orders.items():
            all_orders.append((oid, meta.get("step", 0), "SELL"))
        
        # Sort by step (oldest first)
        all_orders.sort(key=lambda x: x[1])
        
        # Cancel the oldest N
        for i in range(min(count, len(all_orders))):
            oid, _, side = all_orders[i]
            self._cancel_order(oid)
            if side == "BUY":
                self.open_buy_orders.pop(oid, None)
            else:
                self.open_sell_orders.pop(oid, None)

    def _cancel_stale_orders(self, max_age: int = 200):
        """Cancel orders older than max_age steps."""
        stale_buy = [
            oid for oid, meta in self.open_buy_orders.items()
            if self.current_step - meta.get("step", 0) > max_age
        ]
        stale_sell = [
            oid for oid, meta in self.open_sell_orders.items()
            if self.current_step - meta.get("step", 0) > max_age
        ]
        self._cancel_order_ids(stale_buy + stale_sell)
    
    def _send_order(self, order: Dict):
        """Send an order to the exchange."""
        order_id = f"ORD_{self.student_id}_{self.current_step}_{self.orders_sent}"
        
        msg = {
            "order_id": order_id,
            "side": order["side"],
            "price": order["price"],
            "qty": order["qty"]
        }
        
        try:
            self.order_send_times[order_id] = time.time()  # Track send time
            self.order_ws.send(json.dumps(msg))
            self.orders_sent += 1
            
            # Track the open order with step for age tracking
            if order["side"] == "BUY":
                self.open_buy_orders[order_id] = {"price": order["price"], "qty": order["qty"], "step": self.current_step}
            else:
                self.open_sell_orders[order_id] = {"price": order["price"], "qty": order["qty"], "step": self.current_step}
                
        except Exception as e:
            print(f"[{self.student_id}] Send order error: {e}")
    
    def _send_done(self):
        """Signal DONE to advance to the next simulation step."""
        try:
            self.order_ws.send(json.dumps({"action": "DONE"}))
            self.last_done_time = time.time()  # Track when we sent DONE
        except:
            pass
    
    def _on_order_response(self, ws, message: str):
        """Handle order responses and fills."""
        try:
            recv_time = time.time()
            data = json.loads(message)
            msg_type = data.get("type")
            
            if msg_type == "AUTHENTICATED":
                print(f"[{self.student_id}] Authenticated - ready to trade!")
            
            elif msg_type == "FILL":
                qty = data.get("qty", 0)
                price = data.get("price", 0)
                side = data.get("side", "")
                order_id = data.get("order_id", "")
                
                # Measure fill latency
                if order_id in self.order_send_times:
                    fill_latency = (recv_time - self.order_send_times[order_id]) * 1000  # ms
                    self.fill_latencies.append(fill_latency)
                    del self.order_send_times[order_id]
                
                # Remove from open order tracking
                self.open_buy_orders.pop(order_id, None)
                self.open_sell_orders.pop(order_id, None)
                
                # Update inventory and cash flow
                if side == "BUY":
                    self.inventory += qty
                    self.cash_flow -= qty * price  # Spent cash to buy
                else:
                    self.inventory -= qty
                    self.cash_flow += qty * price  # Received cash from selling
                
                # Calculate mark-to-market PnL using mid price
                self.pnl = self.cash_flow + self.inventory * self.last_mid
                
                # Store fill for next log entry
                self.pending_fill = {
                    "side": side,
                    "price": price,
                    "qty": qty,
                    "order_id": order_id
                }
                
                print(f"[{self.student_id}] FILL: {side} {qty} @ {price:.2f} | Inventory: {self.inventory} | PnL: {self.pnl:.2f}")
            
            elif msg_type == "ERROR":
                print(f"[{self.student_id}] ERROR: {data.get('message')}")
                
        except Exception as e:
            print(f"[{self.student_id}] Order response error: {e}")
    
    # =========================================================================
    # ERROR HANDLING
    # =========================================================================
    
    def _on_error(self, ws, error):
        if self.running:
            print(f"[{self.student_id}] WebSocket error: {error}")
    
    def _on_close(self, ws, close_status_code, close_msg):
        self.running = False
        print(f"[{self.student_id}] Connection closed (status: {close_status_code})")
    
    # =========================================================================
    # MAIN RUN LOOP
    # =========================================================================
    
    def run(self):
        """Main entry point - register, connect, and run."""
        # Step 1: Register
        if not self.register():
            return
        
        # Step 2: Connect
        if not self.connect():
            return
        
        # Step 3: Run until complete
        print(f"[{self.student_id}] Running... Press Ctrl+C to stop")
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n[{self.student_id}] Stopped by user")
        finally:
            self.running = False
            if self.market_ws:
                self.market_ws.close()
            if self.order_ws:
                self.order_ws.close()
            
            # Close logger
            if self.logger:
                self.logger.close()
                log_path = self.logger.get_filepath()
            else:
                log_path = None
            
            print(f"\n[{self.student_id}] Final Results:")
            print(f"  Orders Sent: {self.orders_sent}")
            print(f"  Inventory: {self.inventory}")
            print(f"  PnL: {self.pnl:.2f}")
            if log_path:
                print(f"  Data logged to: {log_path}")
            
            # Print latency statistics
            if self.step_latencies:
                print(f"\n  Step Latency (ms):")
                print(f"    Min: {min(self.step_latencies):.1f}")
                print(f"    Max: {max(self.step_latencies):.1f}")
                print(f"    Avg: {sum(self.step_latencies)/len(self.step_latencies):.1f}")
            
            if self.fill_latencies:
                print(f"\n  Fill Latency (ms):")
                print(f"    Min: {min(self.fill_latencies):.1f}")
                print(f"    Max: {max(self.fill_latencies):.1f}")
                print(f"    Avg: {sum(self.fill_latencies)/len(self.fill_latencies):.1f}")


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Student Trading Algorithm",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Local server:
    python student_algorithm.py --name team_alpha --password secret123 --scenario normal_market
    
  Deployed server (HTTPS):
    python student_algorithm.py --name team_alpha --password secret123 --scenario normal_market --host 3.98.52.120:8433 --secure
        """
    )
    
    parser.add_argument("--name", required=True, help="Your team name")
    parser.add_argument("--password", required=True, help="Your team password")
    parser.add_argument("--scenario", default="normal_market", help="Scenario to run")
    parser.add_argument("--host", default="localhost:8080", help="Server host:port")
    parser.add_argument("--secure", action="store_true", help="Use HTTPS/WSS (for deployed servers)")
    args = parser.parse_args()
    
    bot = TradingBot(
        student_id=args.name,
        host=args.host,
        scenario=args.scenario,
        password=args.password,
        secure=args.secure
    )
    
    bot.run()
