# Build an AI-assisted MetaTrader 5 trading bot

You are an MQL5 and Python engineer. You are building a trading bot for one trader, who will run it in their own MetaTrader 5 terminal.

## What to build

A working MetaTrader 5 expert advisor in which proven rule-based engines propose trades, an AI layer makes the entries and exits more intelligent and flexible than fixed rules, and a deterministic risk guard has the final say.

Performance target: 50% a year or more, with a normal worst drawdown of 25% or less. A 75% drawdown is tolerable only as a rare event. The trader treats this target as reachable. Your job is to build the bot that gets there and to report what it measures, not to judge whether the target is possible.

## Architecture

Three layers. They are separated so that the AI can improve decisions but can never break a risk limit or stop the bot from running.

**1. Core engines** generate candidate setups and default exits. Start with the three engines listed under "Core engines".

**2. AI layer**, in two parts:

- **Decision model (ONNX).** Trained in Python, loaded natively by the expert advisor, so it also runs in the Strategy Tester. For each candidate setup it decides: take or skip, size as a fraction of the cap, and entry style (enter now, or wait for a better price with a limit order inside the engine's entry window). For each open trade it decides: hold, tighten the stop, trail, take a partial, exit now, or extend a profitable trade past the engine's time exit.
- **LLM advisor (WebRequest).** On a schedule and around scheduled events, it receives a compact snapshot (prices, ATR, open positions, engine states, upcoming FOMC, payrolls and CPI releases, and news headlines if a feed is available). It returns strict JSON: a regime label per market, a risk multiplier between 0 and 1, engines to pause, and exit advice for open positions. The endpoint URL, model name and API key are expert-advisor inputs. Never write a key into source code or logs.

**3. Risk guard**, plain MQL5, applied after the AI:

- Every order carries a hard stop at the broker from the moment it is placed.
- The AI may skip, shrink, delay, tighten, trail, take partials and exit early. It may extend a trade only if the stop is at breakeven or better.
- The AI may not widen a stop beyond the initial 1R, raise size above the cap, remove a stop, or add to a position beyond an engine's own levels.
- One stop-out of the capped-averaging engine costs at most 10% of equity. Daily and total loss limits are inputs.
- If an AI answer is missing, late, malformed or out of range, use the core engine's own rule and log the event. The bot must trade correctly with the AI layer switched off.

## Data, clock and costs

- Hugging Face datasets `bunqi/OANDA_*`, for example `bunqi/OANDA_XAUUSD_Gold`, `bunqi/OANDA_SPX500USD_US-SPX-500`, `bunqi/OANDA_AUDNZD_AUDNZD`. Monthly parquet files in folders `1`, `5`, `60`, `D`. Columns: `time` (unix seconds, UTC), `open`, `high`, `low`, `close`, `volume`. Mid prices, 2006 to Nov 2026.
- Server clock = New York time + 7 hours, following New York daylight saving. Daily bars roll at 17:00 New York, which is 00:00 server time. Make the server offset and every symbol name an input, because brokers differ.
- 1R = the initial stop distance. ATR = Wilder ATR(20) on daily bars, from the prior completed day.

| Market | Round trip | Extra slippage on stop exits |
|---|---|---|
| Gold | max($0.35, 1 bp of price) | $0.10 |
| SPX500 | 0.7 points | 0.25 points |
| NAS100 | 2.0 points | 1.0 points |
| US30 | 3.0 points | 2.0 points |
| DE30 | 2.0 points | 1.0 points |
| FX majors | 1.5 pips | 0.2 pips |
| AUD/NZD/CAD crosses | 2.5 pips | 0.2 pips |

## Core engines

Hours are server time. Targets are for Jan 2018 onward with the AI layer off.

1. **Gold trend-day.** At the open of hours 16 to 19, if price is 1.2 to 3.0 ATR from the day's open, enter in the direction of the move. Stop 0.6 ATR. Exit at 22:55. One trade a day. Target: 172 trades, +0.110R per trade, profit factor 1.49.
2. **Oversold close, long only, SPX500 and US30.** Buy at the close when (C-L)/(H-L) < 0.2. Sell at a close where that ratio is > 0.8, or the close is above the prior day's high, or after 5 days. Stop 3 ATR. Target Sharpe: 0.63 (SPX500), 0.48 (US30).
3. **Capped averaging, AUDNZD, AUDCAD, NZDCAD, hourly.** When the last close is 2 or more ATR from its 100-hour average, fade it. Add at each further 1 ATR, 4 levels, each 1.5x the size of the last. Exit when price reaches 0.5 ATR of profit from the average entry price. Hard stop at 4 ATR from the first entry. Target: Sharpe 0.53, 139 baskets, 3 stop-outs.

You may add engines if they pass the same tests as these three. If a rule above admits two readings, record the reading you used.

## How the AI is trained and tested

These rules keep the measured numbers trustworthy, because the trader will size real money from them.

- **Design period**: Apr 2006 to Dec 2017. **Out of sample**: Jan 2018 to Nov 2026. Fit and tune the decision model on design data only, with walk-forward validation, across at most 200 configurations. Then freeze it and run out of sample once.
- **No look-ahead.** Features use only bars completed before the decision.
- **Keep the decision model only if it earns its place on design data**: the engines with the model must beat the engines without it at double costs. Report the out-of-sample comparison either way.
- **The LLM advisor cannot be backtested.** WebRequest does not run in the Strategy Tester, and an LLM has already read the market history it was trained on. So build a shadow mode, in which the advisor's answers are logged next to what the bot actually did without affecting trades, and a replay mode, in which the tester reads answers from a log file. State that the advisor's effect is unmeasured until it has run forward on a demo account.
- **Parity.** The expert advisor in the Strategy Tester and the Python backtest must agree on the core engines. Re-simulate 30 randomly chosen trades from raw bars with separately written code; entry, exit and P&L must match.

## Order of work

The order matters because each stage validates the one after it.

1. Reproduce the three core engines in Python. If any target metric is off by more than 15% (for the stop-out count, by more than one), stop and report instead of continuing.
2. Train and freeze the decision model. Export it to ONNX.
3. Write the expert advisor: engines, decision model, LLM advisor with shadow and replay modes, risk guard, logging of every decision with its inputs.
4. Compile it and run it in the Strategy Tester. Check parity.
5. Measure and report.

## Safety

- You place no live orders and open no broker connection. Testing happens in Python and the Strategy Tester.
- The expert advisor ships with an input `AllowLiveTrading = false` and refuses to trade on a real account until the trader changes it.
- Publish nothing.

## Deliverables

- The expert advisor source (`.mq5` and include files), the ONNX model, and the Python code for training and backtesting.
- `README.md`: installation, every input, how to allow the LLM endpoint in the terminal's WebRequest list, how to run the tester, and how to run shadow mode on a demo account.
- `RESULTS.md`, in this order:
  1. One line: the annual return the bot reaches at a 25% median worst drawdown, and whether that meets 50%. If not, the gap and the three changes most likely to close it.
  2. A table: engines alone versus engines with the decision model, design and out of sample, at normal and double costs.
  3. Block bootstrap of out-of-sample daily P&L (21-day blocks, 10-year paths): return at the volatility where the median worst drawdown is 25%, the share of paths with a drawdown beyond 75%, and the volatility and drawdown needed for 30% a year.
  4. The parity table.
  5. What you could not verify.

## If something blocks you

- If a dataset cannot be downloaded, stop and say which one. Do not substitute other data.
- If you cannot compile or run MQL5 in this environment, say so plainly. Deliver the source marked as uncompiled, with a compile-and-test checklist for the trader, and do not describe it as working.
- If no LLM endpoint is available to you, build the advisor against a documented JSON contract with a mock, and list it as untested.
