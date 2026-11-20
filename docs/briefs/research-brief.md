# MT5 strategy research brief

You are a quantitative researcher working in a Python environment with a shell and network access. Your reader is one trader who will later turn your findings into a MetaTrader 5 expert advisor.

## Goal

Find out whether a portfolio of rule-based engines, all tradable in MetaTrader 5, can return 50% a year or more while its normal worst drawdown stays at 25% or less. A 75% drawdown is tolerable only as a rare event.

This phase is research only. You deliver evidence and a verdict, not an expert advisor. Place no live orders, open no broker connections, and publish nothing.

"The target is not reachable under this protocol" is a valid and useful result. Real money will be sized from this report, so a faithful negative is worth more than a positive reached by loosening any rule below.

## Data

- Hugging Face datasets `bunqi/OANDA_*`, for example `bunqi/OANDA_XAUUSD_Gold`, `bunqi/OANDA_SPX500USD_US-SPX-500`, `bunqi/OANDA_AUDNZD_AUDNZD`.
- Monthly parquet files in folders `1`, `5`, `60`, `D` (1-minute, 5-minute, hourly, daily bars).
- Columns: `time` (unix seconds, UTC), `open`, `high`, `low`, `close`, `volume`.
- Prices are mid prices, 2006 to Nov 2026. Stops trigger on mid; costs are added separately.
- Server clock = New York time + 7 hours, following New York daylight saving. Daily bars roll at 17:00 New York, which is 00:00 server time. All hours in this brief are server time unless marked otherwise.

## Costs (apply to every test, including reproductions)

| Market | Round trip | Extra slippage on stop exits |
|---|---|---|
| Gold | max($0.35, 1 bp of price) | $0.10 |
| SPX500 | 0.7 points | 0.25 points |
| NAS100 | 2.0 points | 1.0 points |
| US30 | 3.0 points | 2.0 points |
| DE30 | 2.0 points | 1.0 points |
| FX majors | 1.0 to 1.5 pips | 0.2 pips |
| AUD/NZD/CAD crosses | 2.2 to 2.5 pips | 0.2 pips |

Where a range is given, use the upper end unless you can justify a per-pair figure, and record the figure used.

## Definitions

- **1R** = the initial stop distance of a trade.
- **ATR** = Wilder ATR(20) on daily bars, taken from the prior completed day.
- **Design period**: Apr 2006 to Dec 2017. **Out of sample**: Jan 2018 to Nov 2026.
- **Idea** = one trading concept. **Trial** = one idea applied to one market, or to one set of markets declared in advance, and taken to a frozen run.
- **Frozen run** = the single out-of-sample run of a trial, made after its rules and settings are fixed and written to the log.
- **t** = t-statistic of the mean trade result in R on design data (for a sleeve that is always in the market, of the mean daily return).

## Protocol

These rules are fixed. Each exists to keep the out-of-sample numbers honest, so apply the reason as well as the letter when a case comes up that the rule does not name.

1. **Out-of-sample data is touched once per trial.** Make every choice on design data. Explore at most 200 settings per idea there, pick one, write the rules and settings to the log, then make the frozen run. Do not rerun or adjust after seeing an out-of-sample result, because a second look turns out-of-sample data into design data.
2. **Trial budget: at most 32 trials across all of Step 1.** Step 0 reproductions do not count. The budget exists because the number of things tried decides how much the winners can be trusted.
3. **Log every trial in `TRIALS.md`, including failures and ideas abandoned on design data.** Write the entry (idea, markets, settings explored, chosen setting) before the frozen run and add the results after it. Re-read this file before starting each new trial; it is your record of the budget and of what has already been tried.
4. **An engine passes only on design data:** t >= 1.5, at least 150 trades, still net positive at double costs, and no look-ahead. Out-of-sample results are reported for every trial but never admit an engine to, or remove it from, the pre-registered basket.
5. **No look-ahead.** A signal may use only bars completed before the order is placed. Outside data may be used only from its public release time: COT positions are measured on Tuesday and released Friday 15:30 New York, and event rules may use only the scheduled date and time that was known in advance.
6. **Independent check after every run.** Re-simulate 30 randomly chosen trades from raw bars with separately written code that shares no functions with the backtester. Entry, exit and P&L must match. On a mismatch, fix the bug, log it, and rerun; if the fix changes a frozen result, report both numbers.

## Step 0: reproduce three known engines

Do this first, because it validates the simulator, the clock conversion and the cost model before any new trial spends budget. Compare each result to its target for Jan 2018 onward. If any target metric is off by more than 15% (for the stop-out count, by more than one), stop and report what you found instead of continuing. If a rule below admits two readings, record the reading you used.

1. **Gold trend-day.** At the open of server hours 16 to 19, if price is 1.2 to 3.0 ATR from the day's open, enter in the direction of the move. Stop 0.6 ATR. Exit at 22:55. One trade a day.
   Target: 172 trades, +0.110R per trade, profit factor 1.49.
2. **Oversold close, long only, SPX500 and US30.** Buy at the close when (C-L)/(H-L) < 0.2. Sell at a close where that ratio is > 0.8, or the close is above the prior day's high, or after 5 days. Stop 3 ATR.
   Target Sharpe: 0.63 (SPX500), 0.48 (US30).
3. **Capped averaging, AUDNZD, AUDCAD, NZDCAD, hourly.** When the last close is 2 or more ATR from its 100-hour average, fade it. Add at each further 1 ATR, 4 levels, each 1.5x the size of the last. Exit when price reaches 0.5 ATR of profit from the average entry price. Hard stop at 4 ATR from the first entry.
   Target: Sharpe 0.53, 139 baskets, 3 stop-outs.

## Step 1: new trials, in this order

The order is the trader's priority, so that the budget is spent on these first if it runs short.

a. Noise-area intraday momentum on SPX500 and NAS100, 5-minute bars, following Zarattini, Aziz and Barbon (2024), "Beat the Market: An Effective Intraday Momentum Strategy for S&P500 ETF (SPY)". Read the paper and note every change you make to adapt it to CFDs.
b. Multi-speed trend sleeve across gold, indices and FX, with overnight financing charged. State the financing rates and markup you assumed.
c. A positioning rule built on CFTC Commitments of Traders data (download the public files).
d. Event-day rules for FOMC decisions, non-farm payrolls and CPI.
e. Up to 16 ideas of your own. Each must be uncorrelated with the three Step 0 engines: absolute correlation of daily P&L below 0.3 on design data.

## Step 2: portfolio

- Build daily P&L per engine. Set weights from design data only.
- Size any negative-skew engine (the capped-averaging engine is one) so that a single stop-out costs at most 10% of equity.
- Report two baskets side by side: the **pre-registered basket**, which is every engine that passed on design data, and any **hindsight pick**, labelled as hindsight.
- Block bootstrap of out-of-sample daily P&L (21-day blocks, 10-year paths). For each basket report:
  - the annual return at the volatility where the median worst drawdown is 25%, and the share of paths at that volatility with a drawdown beyond 75%;
  - the volatility and median worst drawdown needed for 30% a year.

## When to stop

- Stop when the pre-registered basket reaches a Sharpe of 2.5 on design data, or when the trial budget is spent, whichever comes first.
- If a dataset or outside source cannot be downloaded, stop and report which one. Do not substitute other data or continue on a partial set without saying so.

## Deliverable

`RESULTS.md`, with `TRIALS.md` and the code that produced both, containing in this order:

1. A one-line verdict against the goal: does the pre-registered basket reach 50% a year at a 25% median worst drawdown, yes or no, with the number.
2. One table of every trial: design metrics next to out-of-sample metrics, pass or fail, including failures.
3. The portfolio table from Step 2, both baskets.
4. What you could not verify: assumptions made, readings chosen for ambiguous rules, data gaps, and anything the independent check did not cover.
