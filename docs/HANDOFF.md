# Handoff: what is already known (as of 20 Nov 2026)

Everything here was measured or read in earlier sessions. Each item says where it came from. Treat numbers as claims to re-check, not as facts to build on.

## 1. Sources

| Source | What it is | Read in full? |
|---|---|---|
| `docs/briefs/research-brief.md` | The research protocol (design/out-of-sample split, 32-trial budget, pass rule, Step 0 targets) | Yes |
| `docs/briefs/ai-bot-brief.md` | The build brief (engines, ONNX decision model, LLM advisor, risk guard) | Yes |
| "Keel XAU" document (Claude Mythos, trader's first account) | Business plan and test report for a gold-only EA | Yes. Its `KeelXAU.mq5` source and trade list were not available. |
| "Benchmark and blueprint" document (Claude Mythos, trader's second account) | Study of top mql5.com EAs plus an architecture | No. Only the conversation that produced it was seen. |
| GPT `GoldRangeNY` conversation | Six gold EAs benchmarked; a New York morning range-breakout EA written | Summary only. The `.mq5` and three `.md` files were not available. |
| `research/` in this repo | Step 0 reproduction code and outputs | Yes (written in the session that produced this file) |

## 2. What the trader has said they want

| Topic | Research and bot briefs | Later conversation (second Mythos account) | Open? |
|---|---|---|---|
| Return target | 50% a year at a 25% normal worst drawdown; 75% drawdown only as a rare event | "Over 75% annual return", higher than QQQ | Yes |
| Markets | Gold, index CFDs, FX | All of those, with capital moved to whichever instrument is most profitable | No conflict |
| Styles | Rule-based engines | Opening range breakout, scalping, swing, volatility and fundamental views | No conflict; each is a trial |
| AI | ONNX decision model plus an LLM advisor that can only lower risk | An LLM analyst reading news and fundamentals to decide "when to go big", possibly a small in-house analyst model | Yes: "go big" versus a hard size cap |
| Who uses it | One trader, own terminal | "Customers" pointed to Claude, GPT or Gemini | Yes |
| Broker | None named; OANDA mid-price data | Coinexx demo, probably on a VPS | Yes |
| Live trading | None | Demo for now | No conflict |

## 3. Results from earlier work

### Keel XAU (Mythos)

- The gold trend-day rule is the only one of seven rule families that survived. Out of sample (2018 to Nov 2026): 172 trades, +0.110R, profit factor 1.49. Design: 166 trades, +0.252R, profit factor 2.44. Hourly bars.
- In money terms that is about 2% a year at 1% risk per trade, about 19 trades a year, with 2018 to 2022 flat.
- It repeated on a second price feed (ejtraderLabs, 2012 to 2022): 142 shared trade days, same direction every time.
- Tried and rejected on design data: daily breakout trend-following on gold and on 13 markets (profit factor 1.00 to 1.06); volatility breakout from the day's open; holding gold above its 200-day average; buying pullbacks in a trend; gold's fixing-hour pattern (gone after 2014); fading large intraday moves in AUDNZD, AUDCAD and NZDCAD with a hard stop (+0.04R, +0.006R at double costs).
- The gold rule did not transfer: silver +0.06R and EURUSD +0.07R on design data, both weak; ten other FX pairs flat or negative.
- `KeelXAU.mq5` (935 lines) was never compiled. Its AI prompt was never run on a model.

These seven families were tried on the same design data this project uses. They sit outside the 32-trial budget, but they are part of the count of things tried and belong in `TRIALS.md` as prior work.

### Benchmark and blueprint (Mythos, second account), from the conversation only

- Most 600% to 900% "growth" figures on mql5.com come from tiny accounts, grid or martingale bots, or backtests. Nearly all the leaders trade only gold.
- Proposed architecture: MT5 EA for execution and risk, a Python side with a small quant model and an LLM analyst, and a capital allocator. Data feeds estimated at about $150 a month.
- Its four closing questions to the trader were not seen. The most important was the maximum acceptable drawdown.

### GoldRangeNY (GPT)

- Rule: measure the 08:20 to 08:50 New York gold range, enter on a 5-minute close beyond it, stop at the range midpoint, target 1.75R, flat at 15:45 New York, 0.25% risk, one entry a day.
- Never backtested on price data, never compiled. It is an untested idea and would cost one trial under Step 1e. It trades gold intraday in New York hours, so check its correlation with the gold trend-day engine first.

## 4. Step 0 reproduction (this repo, `research/`)

Run on 20 Nov 2026 with the costs in the research brief. Targets are for Jan 2018 onward.

| Engine | Target | Measured | Within 15%? |
|---|---|---|---|
| Gold trend-day | 172 trades, +0.110R, PF 1.49 | 172 trades, +0.103R, PF 1.45 | Yes |
| Oversold close, SPX500 | Sharpe 0.63 | Sharpe 0.65 (289 trades) | Yes |
| Oversold close, US30 | Sharpe 0.48 | Sharpe 0.42 (291 trades) | Yes, 12.5% low |
| Capped averaging, 3 pairs | Sharpe 0.53, 139 baskets, 3 stop-outs | Sharpe 0.80, 148 baskets, 2 stop-outs | **No: Sharpe is 51% high** |

Design-period figures from the same runs:

| Engine | Trades | t | Other |
|---|---|---|---|
| Gold trend-day | 166 | 3.51 | +0.238R, PF 2.32; +0.201R at double costs |
| Oversold close, SPX500 | 372 | 2.97 | Sharpe 0.69; t 2.32 at double costs |
| Oversold close, US30 | 369 | 3.05 | Sharpe 0.85; t 2.73 at double costs |
| Capped averaging | 178 baskets | 6.16 | Sharpe 1.07; one stop-out; +0.038R at double costs |

The averaging engine's t of 6.16 rests on a design period with a single stop-out. It is a negative-skew engine and that t overstates it.

### The open Step 0 problem: capped averaging

- Basket count (6.5% high) and stop-outs (2 against 3, inside the "by more than one" tolerance) pass. Sharpe does not.
- Per-pair Sharpes since 2018 are 0.40 (AUDNZD), 0.40 (AUDCAD) and 0.77 (NZDCAD). Their average is 0.52, close to the 0.53 target. The combined daily P&L gives 0.80. The target may be a per-pair average. This is a guess.
- No surviving basket came near the stop: the worst reached 3.46 ATR against a 4 ATR stop. So the missing third stop-out is a difference in rules, not a near miss.
- Two other readings were tried and changed little: fill at the signal bar's close (148 baskets, 2 stops, Sharpe 0.82); ATR updated daily instead of frozen at basket start (148, 2, 0.87).
- Stop-outs found: AUDNZD June 2015 (design), AUDNZD Nov 2019, AUDCAD 4 Apr 2025.
- Nobody has said where the targets for the oversold-close and averaging engines came from. The gold target came from the Keel document. A reference trade list or reference code would settle this.

The research brief says to stop and report on a mismatch like this. It has been reported to the trader; no decision has come back.

### Readings chosen where a rule admitted two

Gold trend-day (`research/step0_gold.py`):
- 5-minute bars. The day's open is the open of the first bar of the server day.
- The test is made at the open of the bar that starts exactly at 16:00, 17:00, 18:00 and 19:00. The first hour that qualifies is taken; entry is that bar's open.
- The stop is checked on each 5-minute bar's high and low from the entry bar on. A bar that opens beyond the stop fills at its open. Stop fills pay $0.10 slippage.
- Exit is the open of the 22:55 bar.

Oversold close (`research/step0_ibs.py`):
- Daily bars are rebuilt from hourly bars by server date.
- Entry at the signal day's close. The stop is 3 times the ATR through the prior day. It triggers on the daily low; a gap below it fills at the open.
- No re-entry on the bar that exits. No financing charged.
- Daily P&L is marked to market as a fraction of entry price. Sharpe is mean over standard deviation of all days, flat days included, times the square root of 252.

Capped averaging (`research/step0_avg.py`):
- Signal on an hourly close; fill at the next bar's open. ATR is frozen when the basket opens.
- Four entries in total, at the first entry and at 1, 2 and 3 ATR against it, sized 1, 1.5, 2.25 and 3.375. Stop at 4 ATR from the first entry.
- Within one bar the order assumed is adds, then stop, then target. If an add and the target fall in the same bar, the basket exits only if the bar closes beyond the target.
- 1R is the loss if all four levels fill and the stop is hit. Costs are 2.5 pips per unit per round trip.
- One basket per pair at a time.

### Not done

- The 30-trade independent re-simulation has not been run for any Step 0 engine.
- `TRIALS.md` does not exist yet. No Step 1 trial has been run: 0 of 32 spent.
- No financing model, no CFTC data, no event calendar.

## 5. Data notes

- 127 datasets exist under `bunqi/`. Folders are `1`, `5`, `5S`, `60` and `D`.
- File names look like `5/OANDA_XAUUSD_Gold_5_2005-01-01_to_2005-01-31.parquet`. Intraday files are monthly. Daily files are in ten-year chunks, not monthly.
- Each parquet has a `.pod` JSON sidecar with the row count and the first and last candle. Use it to check a download.
- `time` is the bar's open. Daily bars are stamped 17:00 New York.
- The daily files contain a few stub bars that start on a Friday or Saturday (gold: 361 of 5,716). `research/common.py` avoids them by rebuilding daily bars from hourly bars, dropping weekend server dates and days with fewer than four hourly bars.
- First bars: gold 19 Mar 2006; SPX500, NAS100, US30 and DE30 March 2003; AUDNZD May 2004. The last bar seen was 20 Nov 2026, a partial day.
- DE30 has about 42,000 five-minute bars a year until 2018 and about 61,000 from 2019. Its trading hours were extended, so an intraday DE30 rule spans two regimes.
- SPX500 has fewer five-minute bars in 2012 to 2017 (60,000 to 66,000 a year against about 70,000). Check for gaps before trusting intraday results there.
- Download with plain HTTPS from `https://huggingface.co/datasets/bunqi/<repo>/resolve/main/<path>`; it redirects to `us.aws.cdn.hf.co`. `research/download.py` does this with 16 threads and writes one parquet per market and timeframe to the folder named by `MT5_DATA`. Eight markets at three timeframes took about a minute.
- Already fetched in the earlier session (not in the repo; rerun the script): daily, hourly and 5-minute for XAUUSD, SPX500USD, NAS100USD, US30USD, DE30EUR, AUDNZD, AUDCAD, NZDCAD; daily and hourly for 42 more FX, metal, energy, bond and index symbols. No 1-minute data.
- CFTC history files (for example `https://www.cftc.gov/files/dea/history/fut_fin_txt_2020.zip`) return 200 with a browser User-Agent and 403 without one.
- FRED (`https://fred.stlouisfed.org/graph/fredgraph.csv?id=DFF`) was reachable, for financing rates.
