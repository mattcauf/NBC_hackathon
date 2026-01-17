"""
Data Summary Generator
=======================
Generate summary statistics and CSV exports from collected JSONL data.
"""

import json
import csv
import os
import argparse
from pathlib import Path
from typing import List, Dict, Optional
from collections import defaultdict


def load_jsonl(filepath: str) -> List[Dict]:
    """Load JSONL file and return list of records."""
    records = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Warning: Skipping invalid JSON line: {e}")
    return records


def calculate_statistics(records: List[Dict]) -> Dict:
    """Calculate summary statistics from records."""
    if not records:
        return {}
    
    # Extract data
    steps = [r["step"] for r in records]
    bids = [r["market"]["bid"] for r in records if r["market"]["bid"] > 0]
    asks = [r["market"]["ask"] for r in records if r["market"]["ask"] > 0]
    mids = [r["market"]["mid"] for r in records if r["market"]["mid"] > 0]
    spreads = [r["market"]["spread"] for r in records if r["market"]["spread"] > 0]
    
    inventories = [r["state"]["inventory"] for r in records]
    pnls = [r["state"]["pnl"] for r in records]
    cash_flows = [r["state"]["cash_flow"] for r in records]
    
    # Count actions and fills
    actions = [r["action"] for r in records if r["action"]]
    fills = [r["fill"] for r in records if r["fill"]]
    
    buy_actions = sum(1 for a in actions if a.get("side") == "BUY")
    sell_actions = sum(1 for a in actions if a.get("side") == "SELL")
    
    buy_fills = sum(1 for f in fills if f.get("side") == "BUY")
    sell_fills = sum(1 for f in fills if f.get("side") == "SELL")
    
    # Calculate fill rates
    total_actions = len(actions)
    total_fills = len(fills)
    fill_rate = (total_fills / total_actions * 100) if total_actions > 0 else 0
    
    # Calculate statistics
    stats = {
        "scenario": records[0].get("scenario", "unknown"),
        "experiment": records[0].get("experiment", "unknown"),
        "run_id": records[0].get("run_id", "unknown"),
        "mode": records[0].get("mode", "unknown"),
        
        # Steps
        "total_steps": len(records),
        "first_step": min(steps) if steps else 0,
        "last_step": max(steps) if steps else 0,
        
        # Prices
        "min_bid": min(bids) if bids else 0,
        "max_bid": max(bids) if bids else 0,
        "avg_bid": sum(bids) / len(bids) if bids else 0,
        "min_ask": min(asks) if asks else 0,
        "max_ask": max(asks) if asks else 0,
        "avg_ask": sum(asks) / len(asks) if asks else 0,
        "min_mid": min(mids) if mids else 0,
        "max_mid": max(mids) if mids else 0,
        "avg_mid": sum(mids) / len(mids) if mids else 0,
        "mid_range": (max(mids) - min(mids)) if mids else 0,
        
        # Spreads
        "min_spread": min(spreads) if spreads else 0,
        "max_spread": max(spreads) if spreads else 0,
        "avg_spread": sum(spreads) / len(spreads) if spreads else 0,
        
        # Inventory
        "min_inventory": min(inventories) if inventories else 0,
        "max_inventory": max(inventories) if inventories else 0,
        "avg_inventory": sum(inventories) / len(inventories) if inventories else 0,
        "final_inventory": inventories[-1] if inventories else 0,
        
        # PnL
        "min_pnl": min(pnls) if pnls else 0,
        "max_pnl": max(pnls) if pnls else 0,
        "final_pnl": pnls[-1] if pnls else 0,
        "avg_pnl": sum(pnls) / len(pnls) if pnls else 0,
        
        # Cash flow
        "final_cash_flow": cash_flows[-1] if cash_flows else 0,
        
        # Trading activity
        "total_actions": total_actions,
        "buy_actions": buy_actions,
        "sell_actions": sell_actions,
        "total_fills": total_fills,
        "buy_fills": buy_fills,
        "sell_fills": sell_fills,
        "fill_rate_pct": fill_rate,
        
        # Fill statistics
        "avg_fill_price": sum(f.get("price", 0) for f in fills) / len(fills) if fills else 0,
        "total_fill_qty": sum(f.get("qty", 0) for f in fills),
        "avg_fill_qty": sum(f.get("qty", 0) for f in fills) / len(fills) if fills else 0,
    }
    
    # Fill latencies
    fill_latencies = [f.get("latency_ms") for f in fills if f.get("latency_ms") is not None]
    if fill_latencies:
        stats["min_fill_latency_ms"] = min(fill_latencies)
        stats["max_fill_latency_ms"] = max(fill_latencies)
        stats["avg_fill_latency_ms"] = sum(fill_latencies) / len(fill_latencies)
    else:
        stats["min_fill_latency_ms"] = 0
        stats["max_fill_latency_ms"] = 0
        stats["avg_fill_latency_ms"] = 0
    
    return stats


def jsonl_to_csv(jsonl_path: str, csv_path: str):
    """
    Convert JSONL file to CSV format for easy analysis.
    
    Flattens nested structure into columns.
    """
    records = load_jsonl(jsonl_path)
    
    if not records:
        print(f"Warning: No records found in {jsonl_path}")
        return
    
    with open(csv_path, 'w', newline='') as f_out:
        writer = None
        
        for record in records:
            # Flatten the nested structure
            flat = {
                "step": record.get("step", 0),
                "timestamp": record.get("timestamp", ""),
                "scenario": record.get("scenario", ""),
                "experiment": record.get("experiment", ""),
                "run_id": record.get("run_id", ""),
                "mode": record.get("mode", ""),
                
                # Market data
                "bid": record.get("market", {}).get("bid", 0),
                "ask": record.get("market", {}).get("ask", 0),
                "mid": record.get("market", {}).get("mid", 0),
                "spread": record.get("market", {}).get("spread", 0),
                "last_trade": record.get("market", {}).get("last_trade", 0),
                
                # Book data
                "bid_depth": record.get("book", {}).get("bid_depth", 0),
                "ask_depth": record.get("book", {}).get("ask_depth", 0),
                
                # State
                "inventory": record.get("state", {}).get("inventory", 0),
                "cash_flow": record.get("state", {}).get("cash_flow", 0),
                "pnl": record.get("state", {}).get("pnl", 0),
                "orders_sent": record.get("state", {}).get("orders_sent", 0),
                
                # Action
                "action_side": record.get("action", {}).get("side", "") if record.get("action") else "",
                "action_price": record.get("action", {}).get("price", 0) if record.get("action") else 0,
                "action_qty": record.get("action", {}).get("qty", 0) if record.get("action") else 0,
                
                # Fill
                "fill_side": record.get("fill", {}).get("side", "") if record.get("fill") else "",
                "fill_price": record.get("fill", {}).get("price", 0) if record.get("fill") else 0,
                "fill_qty": record.get("fill", {}).get("qty", 0) if record.get("fill") else 0,
                "fill_latency_ms": record.get("fill", {}).get("latency_ms", 0) if record.get("fill") else 0,
            }
            
            if writer is None:
                writer = csv.DictWriter(f_out, fieldnames=flat.keys())
                writer.writeheader()
            
            writer.writerow(flat)
    
    print(f"Exported CSV: {csv_path}")


def generate_summary_report(data_dir: str = "data/raw", output_file: str = "data/processed/summary_report.csv"):
    """
    Generate summary report from all JSONL files in data directory.
    
    Creates a CSV with one row per experiment run.
    """
    data_path = Path(data_dir)
    if not data_path.exists():
        print(f"Error: Data directory '{data_dir}' does not exist")
        return
    
    # Find all JSONL files
    jsonl_files = list(data_path.glob("*.jsonl"))
    
    if not jsonl_files:
        print(f"No JSONL files found in {data_dir}")
        return
    
    print(f"Found {len(jsonl_files)} JSONL files")
    
    # Process each file
    all_stats = []
    for jsonl_file in jsonl_files:
        print(f"Processing {jsonl_file.name}...")
        records = load_jsonl(str(jsonl_file))
        stats = calculate_statistics(records)
        stats["source_file"] = jsonl_file.name
        all_stats.append(stats)
    
    # Write summary CSV
    if all_stats:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=all_stats[0].keys())
            writer.writeheader()
            writer.writerows(all_stats)
        
        print(f"\nSummary report written to: {output_path}")
        print(f"Total experiments: {len(all_stats)}")
    else:
        print("No statistics generated")


def process_single_file(jsonl_path: str, generate_csv: bool = True, generate_stats: bool = True):
    """Process a single JSONL file."""
    if not os.path.exists(jsonl_path):
        print(f"Error: File '{jsonl_path}' does not exist")
        return
    
    records = load_jsonl(jsonl_path)
    print(f"Loaded {len(records)} records from {jsonl_path}")
    
    if generate_stats:
        stats = calculate_statistics(records)
        print("\nSummary Statistics:")
        print("=" * 70)
        for key, value in stats.items():
            if isinstance(value, float):
                print(f"  {key:30}: {value:12.2f}")
            else:
                print(f"  {key:30}: {value}")
        print("=" * 70)
    
    if generate_csv:
        # Save CSV to processed directory
        jsonl_file = Path(jsonl_path)
        csv_path = Path("data/processed") / jsonl_file.with_suffix(".csv").name
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        jsonl_to_csv(jsonl_path, str(csv_path))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate summaries and CSV exports from JSONL data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process single file
  python -m analysis.summary --file data/raw/normal_market_passive_20240117_100000.jsonl
  
  # Generate summary report for all files
  python -m analysis.summary --summary
  
  # Convert all JSONL to CSV
  python -m analysis.summary --convert-all
  
  # Process directory
  python -m analysis.summary --dir data/raw
        """
    )
    
    parser.add_argument("--file", help="Process single JSONL file")
    parser.add_argument("--dir", default="data/raw", help="Data directory (default: data/raw)")
    parser.add_argument("--summary", action="store_true", help="Generate summary report")
    parser.add_argument("--convert-all", action="store_true", help="Convert all JSONL files to CSV")
    parser.add_argument("--output", default="data/processed/summary_report.csv", help="Output file for summary report")
    
    args = parser.parse_args()
    
    if args.file:
        process_single_file(args.file)
    elif args.summary:
        generate_summary_report(data_dir=args.dir, output_file=args.output)
    elif args.convert_all:
        data_path = Path(args.dir)
        jsonl_files = list(data_path.glob("*.jsonl"))
        for jsonl_file in jsonl_files:
            csv_path = Path("data/processed") / jsonl_file.with_suffix(".csv").name
            csv_path.parent.mkdir(parents=True, exist_ok=True)
            jsonl_to_csv(str(jsonl_file), str(csv_path))
        print(f"\nConverted {len(jsonl_files)} files to CSV")
    else:
        # Default: generate summary report
        generate_summary_report(data_dir=args.dir, output_file=args.output)

