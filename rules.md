Evan
lamber11.
Online
yash
This is the start of the #national-bank channel. 
Samuel-Martineau — 11:25 AM
@Sam - National Bank Where can we learn more about the National Bank High-Frequency Trading Strategy Development Competition?
Matthieu_NBC — 11:31 AM
Hi, 

Competition Connection Details
To participate in the National Bank High-Frequency Trading Strategy Development Competition, use the following technical specifications:
Leaderboard    https://3.98.52.120:8433/api/
QuickStart GitHub Repository https://github.com/mattcauf/NBC_hackathon
python student_algorithm.py --host 3.98.52.120:8433 --scenario normal_market --name team_alpha --password secret123 --secure
🔑 Access Instructions
Before you can start sending orders to the API, you must be authorized
Provide your team name we will send you back a password. 
GitHub
GitHub - mattcauf/NBC_hackathon
Contribute to mattcauf/NBC_hackathon development by creating an account on GitHub.
GitHub - mattcauf/NBC_hackathon
Samuel-Martineau — 11:32 AM
There seems to be an SSL error with the API endpoint
Matthieu_NBC — 11:32 AM
you have to trust it
Samuel-Martineau — 11:33 AM
I did, but the SSL connection still yields an PR_CONNECT_RESET_ERROR. 
~> curl https://3.98.52.120:8433/api/
curl: (35) Recv failure: Connection reset by peer
Matthieu_NBC — 11:34 AM
use the github repo as a starting point. this https://3.98.52.120:8433/api/ is the leaderboard
Théo — 11:56 AM
where do we provide our team name to be accepted
Matthieu_NBC — 11:56 AM
Dm me
Samuel-Martineau — 11:58 AM
The GitHub repo references a local server, but I don't see a way to run it
Matthieu_NBC — 12:02 PM
3.98.52.120:8433 is the server you need to use
ex python student_algorithm.py --host 3.98.52.120:8433 --scenario normal_market --name team_alpha --password secret123 --secure
[M13] Tavi (Dev Lead) — 12:12 PM
@Hacker National Bank Challenge Details:
# NBC Challenge: Hackathon Brief: Market Making Simulation
## High-Frequency Trading Strategy Development Competition

---

## 🎯 Challenge Overview
Expand
National Bank Challenge.md
4 KB
[M13] Tavi (Dev Lead)
 pinned a message to this channel. See all pinned messages. — 12:12 PM
Matthieu_NBC — 12:17 PM
best pnl, best notional, less aggresive trades and we are checking inventory managment. 
Mingruifu Lin — 12:42 PM
I keep getting the error:

Registration error: ('Connection aborted.', ConnectionResetError(54, 'Connection reset by peer'))
Shan Iyer

 — 12:55 PM
same here what is the exact way to start a manual trade?
python3 manual_trader.py --name <name> --password <pwd> --scenario normal_market --host 3.98.52.120:8433 --secure gives: Error registering: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
and if i omit the last two args i get: Error registering: HTTPConnectionPool(host='localhost', port=8080): Max retries exceeded with url: /api/replays/normal_market/start (Caused by NewConnectionError("HTTPConnection(host='localhost', port=8080): Failed to establish a new connection: [Errno 111] Connection refused"))
Matthieu_NBC — 12:57 PM
I migh need you team name
python  .\manual_trader.py --host 3.98.52.120:8433 --secure --name team --password password
Mingruifu Lin — 12:58 PM
For some reason, it works now.
Shan Iyer

 — 12:58 PM
works now for me too thanks
Matthieu_NBC — 12:58 PM
ok it is the server I had to restart it
﻿
# NBC Challenge: Hackathon Brief: Market Making Simulation
## High-Frequency Trading Strategy Development Competition

---

## 🎯 Challenge Overview

You are **elite market makers** with the fastest network connection on the street. Your mission: **develop a trading algorithm that survives market chaos and generates profit under extreme conditions**.

You see market data before anyone else. You can detect crashes forming in milliseconds. You provide liquidity when it matters most. But you also face the greatest risk—your inventory can explode, your spreads can widen, and a flash crash can wipe out your entire position in seconds.

This is high-frequency trading at its most intense.

---

## 📊 The Game

### Your Objective
```
Build an algorithm that excels across all market conditions.
The best team wins. Period.
```

### What You Control
- **Order submission:** Buy/sell limit orders or market orders
- **Position management:** Adjust inventory, hedge risk
- **Quote adjustment:** Adapt spreads to market conditions
- **Risk discipline:** Stop losses, position limits, inventory caps
- **Speed:** React faster than anyone else to market changes

### Your Competitive Advantage
- **Fastest data feed:** You see market snapshots 100ms before everyone else
- **First-mover advantage:** You can detect crashes and adapt before others react
- **Network efficiency:** Your orders execute with zero latency

### Market Agents
The market is populated with other agents that act on the book like you. Each trade consumes liquidity.
When crashes occur, these agents interact to create cascading effects you must navigate.

---

## 💡 What Wins

The best market makers excel at:
- **Profitability:** Generate strong returns through smart trading
- **Notional Traded:** Trade actively across all conditions
- **Inventory Management:** Maintain light positions to survive crashes
- **Speed:** React faster than competitors to market changes

One team will dominate all four dimensions. That team wins.

---

## 🚀 Technical Setup

### Getting Started

The GitHub repository includes:
- **Python template** for connecting to the exchange simulator
- **Market data handler** for receiving real-time feeds
- **Order submission module** for sending trades

The repo will be communicated in the Discord channel.

---

## 📈 Hackathon Timeline

### Training Phase
Three scenarios will be released representing 15 minutes of market data each.

You can:
- Run them as many times as you wish
- Test different strategies on each scenario
- Dominate all three to prepare for finals

### Finals Format (Last 3 Hours)
One Final scenario will be available 3 hours before the end of the hackathon. It is a full trading day run (6 hours and 30 minutes) - you need to survive it.

**Strategy:** Test your algorithms early. Save your best algorithm for finals.

---

## ⚠️ Rules

### You Can
✅ Use any programming language (Python templates provided)
✅ Use any libraries or AI tools
✅ Submit multiple versions before finals

### You Cannot
❌ Hardcode prices or crashes
❌ Exceed 1 second per decision cycle
❌ Exceed 5000 of inventory shares.

### Finals Rules
❌ One run for the final scenario only

---

## 🚨 Final Words

> **You have the fastest network and the first-mover advantage. The question is: what will you do with it?**

**Test early. Test often. Save your best for finals.**

The first part is your **training ground**. Iterate, refine, optimize.

The last 3 hours are your **championship run**. One scenario, one shot. No second chances.

The best team will be:
- Fast enough to see crashes coming
- Smart enough to manage inventory
- Active enough to provide liquidity
- Disciplined enough to survive

Speed is your advantage. Risk management is your survival. Active market making is your business.

**The best team wins.**