# Which Broker Should I use for Trading Options?

> Updated: *December 2025*

I would like to sell some options for income.

And I figured I should probably not do it on Robinhood - - Robinhood is famous for offering "free" trading, but charging wholesalers a PFOF[^1] fee for the privilege of routing your orders to them. They usually charge somewhere between $0.3 - $1.2 per contract, dependon on spread. And I think this fee comes back to us.

[^1]: PFOF = Pay For Order Flow; basically, a rebate for directing customers' trades to them.

So I[^2] made the following tables to figure out what different brokerages charge for trading with them. Note that fees + PFOF probably doesn't give a full picture of how much it actually costs. For one, the wholesaler behind your brokerage might be making much more money off the spread than it rebates back to your brokerage via PFOF. For another, "zero total cost" in these table might not actually mean anything - - When market makers successfully avoid competing on price by using PFOF to buy order flow, they stop having the incentive to offer good spreads on the market, and the spread is going to get higher whether you go through a broker with PFOF or not - - kindda like how credit card companies charge merchants a fee that make the price higher, even if you pay with cash.

[^2]: Claude, really.

Nevertheless, I want to know what my broker is making off of me, so with those two grains of salt taken, here's the tables:


---


## Total Cost Per Contract (Commission + Hidden PFOF)[^3]

| Broker | Commission | PFOF | **True Cost** | Routes To |
|--------|-----------|------|---------------|-----------|
| **IBKR Pro** | $0.65 | $0.00 | **$0.65** | Exchanges (SmartRouting) |
| **Fidelity** | $0.65 | $0.00 | **$0.65** | Exchanges |
| Schwab | $0.65 | ~$0.39 | ~$1.04 | Citadel 35%, Virtu 22% |
| Tastytrade | $0.50 | ~$0.40 | ~$0.90 | Citadel, Susquehanna, Wolverine |
| Robinhood | $0.00 | ~$0.50 | ~$0.50 | Citadel, Wolverine |
| Alpaca | $0.00 | ~$0.30? | ~$0.30? | Jane Street, Citadel, Virtu |
| Tradier Pro | $0.00 | ~$0.40 | ~$0.40 | Apex → Citadel, Virtu |

[^3]: PFOF estimates from [FINRA 606 Database](https://www.finra.org/finra-data/606-nms-data), [Ernst & Spatt (2022)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4056512), and broker disclosures.

## Fixed Costs to Trade[^4]

Beyond per-trade fees, some brokers charge monthly subscriptions or account maintenance fees:

| Broker | Monthly Fee | Inactivity Fee | Transfer Out |
|--------|-------------|----------------|--------------|
| IBKR Pro | $0 | $0 | $0 |
| Fidelity | $0 | $0 | $0 |
| Schwab | $0 | $0 | $0 |
| Tastytrade | $0 | $0 | $75 |
| Robinhood | $0 | $0 | $100 |
| Alpaca | $0 | $0 | $0 |
| Tradier Pro | **$10/mo** | $50/yr if <$2K | $75 |

Tradier Pro's $10/month adds up fast—$120/year just to access "free" trading.

[^4]: Fee schedules from [IBKR](https://www.interactivebrokers.com/en/pricing/commissions-options.php), [Fidelity](https://www.fidelity.com/trading/commissions-margin-rates), [Schwab](https://www.schwab.com/pricing), [Tastytrade](https://tastytrade.com/pricing/), [Robinhood](https://robinhood.com/us/en/support/articles/trading-fees-on-robinhood/), [Alpaca](https://alpaca.markets/support/what-are-the-fees-associated-with-options-trading), [Tradier](https://tradier.com/individuals/pricing).


---

## What do these costs mean?

To give a better idea what these fees mean in practice, here are some simulations of actual scenarios that might happen in real life.

**Scenario 1: Buy & Hold LEAPs**[^5]

10 contracts, $15,000 position, hold 18 months

| Broker | Total Fees (18 mo) | % of Position |
|--------|-------------------|---------------|
| Alpaca | $6 | 0.04% |
| Robinhood | $10 | 0.07% |
| IBKR Pro | $13 | 0.09% |
| Fidelity | $13 | 0.09% |
| Tastytrade | $16 | 0.11% |
| Schwab | $21 | 0.14% |
| Tradier Pro | $188 | 1.25% |

**Verdict:** Fees are negligible for buy-and-hold. Use **Alpaca** if you want an API, **Fidelity** if you don't. Avoid Tradier Pro—$180 in subscription fees alone eats your "savings."

[^5]: Total = (contracts × 2 × true cost per contract) + subscription fees. Schwab: 20 × $1.04 ≈ $21.

---

**Scenario 2: Selling Cash-Secured Puts**[^6]

1,000 contracts/year, $100K account, $50K premium collected

| Broker | Trading Costs | Margin Interest | **Net Income** |
|--------|--------------|-----------------|----------------|
| **Alpaca** | ~$500 | −$2,375 | **$47,125** |
| Robinhood | ~$500 | −$2,500 | $47,000 |
| IBKR Pro | $650 | −$2,570 | $46,780 |
| Tradier Pro | ~$720 | −$4,750 | $44,530 |
| Fidelity | $650 | −$4,750 | $44,600 |
| Schwab | ~$1,040 | −$4,500 | $44,460 |
| Tastytrade | ~$1,600 | −$4,750 | $43,650 |

**Verdict:** Alpaca wins on pure cost. IBKR Pro is ~$500/year more but offers better execution quality and a mature platform. Both save ~$3,000/year vs Tastytrade.

[^6]: Trading costs = contracts × true cost. Margin interest on $50K: [IBKR](https://www.interactivebrokers.com/en/trading/margin-rates.php) 5.14%, [Robinhood](https://robinhood.com/us/en/support/articles/margin-rates/) 5.0%, [Alpaca](https://alpaca.markets/support/margin-interest-rates) 4.75%, others ~9-10%. 606 reports: [Robinhood](https://cdn.robinhood.com/assets/robinhood/legal/RHS%20SEC%20Rule%20606%20and%20607%20Disclosure.pdf), [Tastytrade](https://tastytrade.com/rule-606-routing-reports/), [Schwab](https://www.schwab.com/legal/order-routing-1).
