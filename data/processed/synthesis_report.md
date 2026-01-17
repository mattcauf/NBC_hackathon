================================================================================
EXPERIMENT SYNTHESIS REPORT
================================================================================
Generated: 2026-01-17 18:40:07
Total Experiments: 13

[1] EFFECTIVENESS RANKINGS
--------------------------------------------------------------------------------

1.1 Profitability Ranking:
Experiment                          | Final PnL | PnL per Fill | Total Fills
----------------------------------------------------------------------------
qty_test_400_offset0.0_freq10       | $21880.00 | $276.96      | 79.0       
qty_test_300_offset0.0_freq10       | $11700.00 | $153.95      | 76.0       
inventory_mgmt_qty100_thresh200_fre | $0.00     | $0.00        | 0.0        
passive                             | $0.00     | $0.00        | 0.0        
price_explore_mid_qty100_freq10     | $0.00     | $0.00        | 0.0        
qty_test_100_offset0.0_freq10       | $0.00     | $0.00        | 0.0        
qty_test_200_offset0.0_freq10       | $0.00     | $0.00        | 0.0        
qty_test_500_offset0.0_freq10       | $0.00     | $0.00        | 0.0        
aggressive_buy_qty100_freq10        | $-250.00  | $-5.95       | 42.0       
aggressive_sell_qty100_freq10       | $-250.00  | $-6.10       | 41.0       

1.2 Notional Traded Ranking:
Experiment                  | Notional Traded | Total Fills | Total Fill Qty
----------------------------------------------------------------------------
spread_cross_qty100_freq10  | $304254330.00   | 3043.0      | 304300.0      
price_explore_ask_qty100_fr | $30696930.00    | 307.0       | 30700.0       
price_explore_bid_qty100_fr | $26294740.00    | 263.0       | 26300.0       
qty_test_400_offset0.0_freq | $7889690.00     | 79.0        | 7900.0        
qty_test_300_offset0.0_freq | $7593090.00     | 76.0        | 7600.0        
aggressive_buy_qty100_freq1 | $4199580.00     | 42.0        | 4200.0        
aggressive_sell_qty100_freq | $4099180.00     | 41.0        | 4100.0        
inventory_mgmt_qty100_thres | $0.00           | 0.0         | 0.0           
passive                     | $0.00           | 0.0         | 0.0           
price_explore_mid_qty100_fr | $0.00           | 0.0         | 0.0           

1.3 Inventory Management Ranking (lower is better):
Experiment                    | Risk Score | Max Inventory | Final Inventory
----------------------------------------------------------------------------
inventory_mgmt_qty100_thresh2 | 0.000      | 0.0           | 0              
passive                       | 0.000      | 0.0           | 0              
price_explore_mid_qty100_freq | 0.000      | 0.0           | 0              
qty_test_100_offset0.0_freq10 | 0.000      | 0.0           | 0              
qty_test_200_offset0.0_freq10 | 0.000      | 0.0           | 0              
qty_test_500_offset0.0_freq10 | 0.000      | 0.0           | 0              
spread_cross_qty100_freq10    | 0.020      | 0.0           | -100           
qty_test_300_offset0.0_freq10 | 0.580      | 900.0         | -2800          
qty_test_400_offset0.0_freq10 | 0.620      | 3100.0        | -1300          
aggressive_buy_qty100_freq10  | 1.000      | 5000.0        | 5000           

1.4 Speed Ranking (lower latency is better):
Experiment           | Avg Latency (ms) | Min Latency (ms) | Max Latency (ms)
-----------------------------------------------------------------------------
qty_test_400_offset0 | 7.53             | 0.00             | 16.25           
price_explore_bid_qt | 7.56             | 0.00             | 21.40           
aggressive_sell_qty1 | 7.61             | 0.00             | 18.14           
spread_cross_qty100_ | 7.78             | 0.00             | 24.84           
qty_test_300_offset0 | 7.78             | 0.00             | 16.46           
price_explore_ask_qt | 8.11             | 0.00             | 33.78           
aggressive_buy_qty10 | 8.97             | 0.00             | 17.98           

1.5 Overall Composite Score:
Experiment           | Composite Score | Final PnL  | Notional Traded | Inventory Risk
--------------------------------------------------------------------------------------
qty_test_400_offset0 | 0.500           | $21880.00  | $7889690.00     | 0.620         
qty_test_300_offset0 | 0.319           | $11700.00  | $7593090.00     | 0.580         
inventory_mgmt_qty10 | 0.300           | $0.00      | $0.00           | 0.000         
passive              | 0.300           | $0.00      | $0.00           | 0.000         
price_explore_mid_qt | 0.300           | $0.00      | $0.00           | 0.000         
qty_test_100_offset0 | 0.300           | $0.00      | $0.00           | 0.000         
qty_test_200_offset0 | 0.300           | $0.00      | $0.00           | 0.000         
qty_test_500_offset0 | 0.300           | $0.00      | $0.00           | 0.000         
spread_cross_qty100_ | 0.180           | $-17995.00 | $304254330.00   | 0.020         
aggressive_sell_qty1 | 0.015           | $-250.00   | $4099180.00     | 1.000         

================================================================================
[2] WHAT WORKED
--------------------------------------------------------------------------------
Experiment           | Reason               | Final PnL  | Fill Rate | Inventory Risk
-------------------------------------------------------------------------------------
qty_test_300_offset0 | Profitable           | $11700.00  | 8.1%      | 0.58          
qty_test_400_offset0 | Profitable           | $21880.00  | 15.2%     | 0.62          
spread_cross_qty100_ | High fill rate, low  | $-17995.00 | 84.6%     | 0.02          

================================================================================
[3] WHAT DIDN'T WORK
--------------------------------------------------------------------------------
Experiment                      | Failure Reason                    
--------------------------------------------------------------------
price_explore_mid_qty100_freq10 | Zero fills despite 3599.0 actions 
qty_test_100_offset0.0_freq10   | Zero fills despite 3599.0 actions 
qty_test_200_offset0.0_freq10   | Zero fills despite 3599.0 actions 
qty_test_500_offset0.0_freq10   | Zero fills despite 197.0 actions  
aggressive_buy_qty100_freq10    | Inventory limit hit (max: 5000.0) 
aggressive_sell_qty100_freq10   | Inventory limit hit (max: 0.0)    
price_explore_ask_qty100_freq10 | Inventory limit hit (max: 35300.0)
price_explore_bid_qty100_freq10 | Inventory limit hit (max: 0.0)    
spread_cross_qty100_freq10      | Large loss: $-17995.00            

================================================================================
[4] SURPRISING FINDINGS
--------------------------------------------------------------------------------

1. Mid-price limit orders never execute
   Experiment: price_explore_mid_qty100_freq10
   Details: Submitted 3599.0 orders at mid-price, got 0 fills
   Implication: Limit orders at mid-price don't execute - need to cross spread or be more aggressive

2. Quantity sweet spot exists
   Experiment: qty_test series
   Details: Qty 300, 400 got fills and profit, but qty 100, 200, 500 got zero fills
   Implication: Optimal quantity is around 300-400 shares, not 100-200 or 500

3. Spread crossing strategy loses money despite high fill rate
   Experiment: spread_cross_qty100_freq10
   Details: 84.6% fill rate but lost $-17995.00
   Implication: Crossing the spread costs money - you pay the spread, not capture it. Need better pricing.

4. Aggressive strategies hit inventory limits very quickly
   Experiment: aggressive_buy/sell
   Details: Hit 5000 inventory limit in ~511.0 steps
   Implication: Need inventory management to prevent hitting limits

5. Market is extremely stable
   Experiment: passive
   Details: Mid price range only 0.10, spread stayed 0.1-0.2
   Implication: Normal market has very tight spreads, making market making challenging

6. Asymmetric fill behavior between bid and ask
   Experiment: price_explore_bid/ask
   Details: Ask exploration: 307.0 fills, $-1765.00 PnL. Bid exploration: 263.0 fills, $-1635.00 PnL
   Implication: Market may have directional bias or different liquidity on each side

================================================================================
[5] STRATEGIC RECOMMENDATIONS
--------------------------------------------------------------------------------
[+] Best performing strategy: qty_test_400_offset0.0_freq10 (PnL: $21880.00)
    -> Consider adapting this approach for production strategy
[-] Avoid strategies that got zero fills:
    -> price_explore_mid_qty100_freq10: Zero fills despite 3599.0 actions
    -> qty_test_100_offset0.0_freq10: Zero fills despite 3599.0 actions
    -> qty_test_200_offset0.0_freq10: Zero fills despite 3599.0 actions
    -> qty_test_500_offset0.0_freq10: Zero fills despite 197.0 actions
[+] Quantity optimization:
    -> Use quantities around 300-400 shares for optimal fill rates
[-] Spread crossing strategy:
    -> Don't cross the spread blindly - need better pricing logic
[!] Critical: Implement inventory management
    -> Multiple strategies hit the 5000 inventory limit
    -> Need dynamic position limits and rebalancing

================================================================================