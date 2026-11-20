# AI-Driven MT5 Platform: Benchmark and Blueprint

Nov 20, 2026. Written by Claude Mythos in an earlier session; copied here unchanged except that the trader's name is replaced by "the trader".

## Summary

We can be competitive by doing what the mql5 leaders don't: trade several instruments and styles with a real news and fundamentals layer, under a hard drawdown cap, with a verified track record. Most top mql5 "growth" figures (600% to 900%) come from tiny accounts, grid or martingale logic, or backtests, so they are not a fair yardstick.

- **Target.** 75%+ a year as the stretch goal, 40% a year with at most 20% drawdown as the gate to go live. Either beats QQQ.
- **Design.** A Python brain (quant model, LLM analyst, strategy sleeves, allocator) decides; a thin MT5 EA executes and enforces risk limits on its own.
- **Data.** About 150 USD a month to start, about 420 USD for the full stack; positioning, short interest, filings and macro data are free.
- **Decisions for the trader** are listed at the end: drawdown cap, own capital vs product, data tier, and a GitHub repository.

## Benchmark: what the mql5 leaders really do

The headline numbers on mql5.com (600% to 900% "growth") are mostly not comparable to a fund return, and none of the top systems shows a multi-year real-money record at 75%+ a year with a drawdown under 20%. The no-grid systems with live data show 7% to 26% in a good month, with drawdowns of 3% to 30%. Three things inflate the leaderboard:

- **Growth is computed on tiny bases with deposits and withdrawals.** The [GoldWave signal](https://www.mql5.com/en/signals/2339082) shows 855% over 77 weeks, but it started from a 50 USD deposit, had 2,000 USD added and withdrawn, and now holds 478 USD. mql5 itself has flagged it for "Too much growth" and inactivity.
- **Grid, martingale and averaging dominate.** The [MT5 Market listing](https://www.mql5.com/en/market/mt5/expert) is full of them (ABS GoldGrid, Quantum StarMan, Burning Grid, Squid Grid AI). They post smooth curves in ranging markets and blow up in strong trends.
- **Most "AI" and best-seller claims are backtests or one good month.** Karat Killer's +7,229% is a 10-year backtest, not live ([BLODSALGO review](https://blodsalgo.com/blog/en/best-eas-gold-trading-2026/)). Many reviews are written by the sellers themselves.

| EA or signal | Instrument | Style | Return (period) | Max drawdown | Notes |
| --- | --- | --- | --- | --- | --- |
| [GoldWave signal](https://www.mql5.com/en/signals/2339082) | Gold | Trend swing, no grid claimed | 855% (77 weeks) | 17.5% equity | Tiny base, cash flows, user reviews report losses |
| Quantum Queen MT5 | Gold | Grid / averaging | +25% (Mar 2026) | \~21% | 4.98 rating, 365 reviews, \~1,499 USD |
| Quantum King EA | Gold | Grid / averaging | +26% (Mar 2026) | \~29% | Flagged very high risk |
| Gold House MT5 | Gold | Not stated | +25% (Mar 2026) | \~3% | One month only |
| TwisterPro Scalper | Gold | Scalping | +22% (Mar 2026) | \~2.5% | One month only |
| Quantum Valkyrie | Gold | Recovery | -11% (Mar 2026) | \~24% | Shows the recovery-style failure mode |
| Growth Killer | Gold + others | Breakout | +182% live (period not given) | Not given | Reviewer is the seller |
| Pivot Killer | Gold | Pivot breakout | +84% live (period not given) | Not given | 499 USD |

Monthly figures come from the [March 2026 reality check](https://www.mql5.com/en/blogs/post/768836), which is written by a competing seller. Top of the [high-rating signal list](https://www.mql5.com/en/signals/mt5/high-rating) today: MSC SuperGold Pro 16 (916% since 2024), World PEACE Multi FX Algo 4 (859% since 2025), Combo Profile 2026 (777%), all priced 30 to 50 USD a month.

**What this means for us.** Almost every leader is a single-instrument gold system. Nobody on the leaderboard runs a multi-asset allocator or a real news and fundamentals layer. That is our gap. To be credibly "better" we should publish a verified real-money signal with a sensible starting balance, no grid or martingale, and a stated drawdown limit, which most competitors cannot show.

## Targets we propose

Keep the trader's 75% a year as the stretch goal, but pair it with a hard drawdown cap, because a return with no drawdown limit is not a target anyone can test. 75% a year is about 4.8% a month compounded. QQQ has returned roughly 18% to 19% a year over the last decade (approximate, from memory, to be confirmed from data in step 2), so even half the stretch goal beats it handily.

| Metric | Pass gate (to go live) | Stretch goal |
| --- | --- | --- |
| Annual return (CAGR) | 40% | 75%+ |
| Max drawdown, equity | 20% | 25% hard cap |
| Return / max drawdown (Calmar) | 2.0 | 3.0 |
| Sharpe ratio | 1.5 | 2.0 |
| Losing months | 4 of 12 or fewer | 3 of 12 or fewer |
| Out-of-sample check | Walk-forward, 2+ years unseen | Plus 3 months live demo |
| Beats QQQ | Yes, on return and on drawdown | Yes |

**Risk rules baked in from day one:** at most 1% of equity at risk per trade by default, a 3% daily loss stop, a 10% weekly stop, and an automatic kill switch at 20% drawdown that flattens everything and pages the trader. "Go big" mode raises risk per trade to at most 2.5% and only when both AI layers agree with high confidence.

## Architecture

The platform splits thinking from doing: a Python "brain" decides what to trade and how much, and a thin MT5 EA executes and enforces hard risk limits even if the brain fails.

&#91;embedded content: platform architecture · data to broker\]

- **Quant model.** A small gradient-boosted tree model (LightGBM) on technical features: multi-timeframe trend, volatility, support and resistance distance, session, spread. It outputs a regime label and per-instrument trade probabilities. Small, fast, retrained weekly.
- **Analyst layer.** An LLM (Claude, GPT or Gemini, swappable behind one interface) reads the calendar, news, earnings and positioning, and returns a structured view per instrument: direction, confidence 0 to 1, horizon, and the data it relied on. A checker rejects any view that cites a number not found in the feeds. Later we can fine-tune a small in-house analyst model on the LLM's best calls.
- **Strategy sleeves.** Rule-based strategies that propose trades with entry, stop and target (next section).
- **Allocator.** Combines sleeve proposals, the regime and the analyst view into position sizes within the risk budget. It starts as simple volatility-scaled weights tilted by recent performance, then can graduate to a learned policy once there is enough history.
- **Risk engine.** Lives inside the EA, so it works even if Python is down. It enforces per-trade, daily, weekly and total drawdown limits and can flatten everything.
- **Feedback.** Every trade, its reasons and its outcome are logged, so each layer is measured on whether it actually improved results.

## Strategy sleeves and how capital moves between them

Each style becomes a "sleeve": a self-contained strategy with its own signals, stops and track record. The allocator gives each sleeve a risk budget every day, so capital flows to whatever is working in the current regime instead of being locked into one style.

| Sleeve | Instruments | Holding time | Edge it tries to capture | Main risk |
| --- | --- | --- | --- | --- |
| Opening Range Breakout | NAS100, US30, GER40, gold | Minutes to hours | First-hour range sets the day's direction on trend days | Chop days, false breaks |
| Volatility breakout | Gold, NAS100, GBPUSD | Hours to 2 days | Squeezes (low volatility) resolve into large moves | Whipsaw after news |
| Trend swing | Majors, gold, indices | Days to weeks | Persistent trends across timeframes | Sharp reversals |
| Mean-reversion scalp | EURUSD, gold in Asia session | Minutes | Overshoots inside a quiet range | Spread and slippage eat the edge |
| Macro / fundamental "go big" | NAS100, gold, USD pairs | Days to weeks | Mispricing after panics, rate or earnings surprises | Being early; event gaps |

**How the allocator decides.** Each morning (and after major news) it takes three inputs: the regime label from the quant model (trending, ranging, high-volatility, crisis), each sleeve's recent risk-adjusted results, and the analyst layer's market view with a confidence score. It then sizes sleeves so that their combined risk stays inside the portfolio budget, with correlation caps (for example NAS100 and US30 longs count as one bet). Scalping runs only where spreads are low enough, and nothing grid- or martingale-like is allowed.

**"Go big" is a rule, not a feeling.** The macro sleeve can raise risk only when (1) the analyst layer has a high-confidence thesis backed by verified data, (2) the technical model confirms (for example a reclaim of support after capitulation), and (3) a defined stop exists. the trader's tech sell-off example is exactly the case it is built for, but its facts get checked against live feeds first.

## Data feeds and what they cost

A lean stack costs about 150 USD a month and the full stack about 420 USD, and a lot of the most useful data (positioning, short interest, filings, macro series) is free. Prices are from published plan pages where linked; rows marked approximate are from memory and get confirmed before we sign up.

| Need | Feed | Price / month | Why we need it |
| --- | --- | --- | --- |
| Forex, gold, index prices (live) | Broker's MT5 feed | Free | What we actually trade on, with the broker's real spread |
| Tick history for backtests | Dukascopy historical ticks | Free (approximate) | 10+ years of ticks for realistic spread and slippage |
| US stocks, ETFs, news (for the analyst) | [Massive, formerly Polygon.io](https://apicostcalc.com/blog/polygon-massive-rebrand-api-pricing.html) Developer / Advanced | 79 / 199 | NVDA, QQQ components, real-time tape for "go big" decisions |
| Fundamentals, earnings, transcripts | [Financial Modeling Prep](https://apis.io/plans/financial-modeling-prep/financial-modeling-prep-plans-pricing/) Premium / Ultimate | 69 / 139 | P/E, growth, earnings dates, call transcripts, 13F holdings |
| Economic calendar and forecasts | [Trading Economics](https://apis.io/plans/tradingeconomics/tradingeconomics-plans-pricing/) Standard | 149 (billed yearly, unconfirmed) | CPI, NFP, FOMC times, consensus and actuals |
| Macro series | FRED (St. Louis Fed) | Free (approximate) | Rates, yields, liquidity, credit spreads |
| Futures positioning | CFTC Commitments of Traders | Free | Who is crowded long or short in gold, currencies, Nasdaq futures |
| Short interest | FINRA short interest | Free, twice monthly (approximate) | Short-squeeze setups like the one the trader described |
| Filings and insider trades | SEC EDGAR | Free | 10-Q, 8-K, Form 4 insider buys |
| Volatility and options sentiment | VIX and VXN from Cboe | Free daily (approximate) | Fear gauge for regime and "go big" timing |
| LLM analyst | Claude, GPT or Gemini API | Tens of USD (approximate) | Reads the above and writes the market view |

**Suggested tiers.** Lean start (step 2 and 3): Massive Developer + FMP Premium + free sources, about 150 USD a month. Full stack (demo trading): add Trading Economics and upgrade Massive to Advanced, about 420 USD a month. Premium newswires such as Benzinga or Bloomberg are quote-only and can wait until the analyst layer proves it adds value. Alpha Vantage (49.99 to 249.99 USD) and Twelve Data (79 USD and up) are fallbacks ([price comparison](https://multiples.vc/compare/api-pricing/md)).

## Infrastructure, broker and VPS

One Windows VPS near the broker's server runs MT5 and the Python brain side by side; heavier model training happens elsewhere.

- **VPS.** Windows Server, 4 vCPU, 8 GB RAM, in the same data centre region as the broker's MT5 server (often London or New York). Roughly 30 to 60 USD a month (approximate). MT5 and the official `MetaTrader5` Python package both need Windows, which is the main reason for Windows here.
- **Link between EA and Python.** The EA talks to the Python service over a local socket (ZeroMQ). The EA stays in charge of execution and hard risk limits, so if Python crashes or the LLM is slow, open trades keep their stops and nothing new opens.
- **Training.** Model training and backtests run on a laptop or a cloud GPU on demand, not on the trading VPS.
- **Broker.** Coinexx is fine for demo. Before real money, compare it with at least one more broker on four points: real spreads and commission on gold and NAS100 at the open, whether indices are offered as CFDs, swap costs on multi-day holds, and regulation and withdrawal reputation (offshore brokers carry counterparty risk). The backtester will use each broker's actual contract specs.
- **Monitoring.** A small web dashboard plus phone alerts for fills, daily P&L, drawdown, and any kill-switch event.
- **LLM cost.** The analyst runs on a schedule (pre-session briefs plus event triggers), not on every tick. Expect tens of dollars a month in API usage at that cadence (approximate; measured in step 3).

## Risks, open questions and step 2

**Biggest risks**

- **Overfitting.** Backtests can always be tuned to look great. Every model is judged only on walk-forward, unseen data, with realistic spread, slippage and swap.
- **Leverage.** At 100:1, a 1% adverse move on a fully levered position wipes the account. Leverage is a ceiling the broker allows, not a setting we use; position size comes from risk per trade.
- **LLM hallucination.** The analyst can state wrong facts confidently. It must cite the feed record behind every number, and the risk engine ignores views it cannot verify.
- **Look-ahead in news.** Historical news must be timestamped to the second it was published, or backtests of the analyst layer will cheat.
- **Broker execution.** Demo fills are kinder than real fills, especially at the US open. Plan a small real-money pilot before scaling.

**Open questions for the trader**

- [ ] Is a 20% to 25% maximum drawdown acceptable as the hard cap next to the 75% stretch goal?
- [ ] Is this for your own capital first, or a product for customers later (a sold EA or an mql5 signal)? It changes how the LLM layer is licensed.
- [ ] Which data budget tier (see Data feeds) do you want to start with?
- [ ] Should we create a GitHub repository now so step 2 code has a home?

**Step 2 will build** (waiting for your go): the data pipeline for 10+ years of gold, major forex and index history; a backtester that models spread, slippage, commission and swap per broker; and baseline tests of ORB, volatility breakout and trend swing, before any AI is added.
