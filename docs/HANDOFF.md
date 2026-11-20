# Handoff: what is already known (as of 20 Nov 2026)

Everything here was measured or read in earlier sessions. Each item says where it came from. Treat numbers as claims to re-check, not as facts to build on.

## 1. Sources

| Source | What it is | Read in full? |
|---|---|---|
| `docs/briefs/research-brief.md` | The research protocol (design/out-of-sample split, 32-trial budget, pass rule, Step 0 targets) | Yes |
| `docs/briefs/ai-bot-brief.md` | The build brief (engines, ONNX decision model, LLM advisor, risk guard) | Yes |
| "Keel XAU" document (Claude Mythos, trader's first account) | Business plan and test report for a gold-only EA | Yes. Its `KeelXAU.mq5` source and trade list were not available. |
| `docs/prior/benchmark-and-blueprint.md` (Claude Mythos, trader's second account) | Study of top mql5.com EAs, proposed targets, architecture, strategy sleeves and data feeds | Yes. Its architecture diagram did not survive the export. |
| GPT `GoldRangeNY` conversation | Six gold EAs benchmarked; a New York morning range-breakout EA written | Summary only. The `.mq5` and three `.md` files were not available. |
| `research/` in this repo | Step 0 reproduction code and outputs | Yes (written in the session that produced this file) |

## 2. What the trader has said they want

| Topic | Research and bot briefs | Blueprint and the conversation behind it | Open? |
|---|---|---|---|
| Return target | 50% a year at a 25% median worst drawdown; 75% drawdown only as a rare event | Gate to go live: 40% a year with at most 20% drawdown. Stretch: 75% or more with a 25% hard cap | Yes |
| Markets | Gold, index CFDs, FX | The same, with capital moved each day to whichever sleeve is working | No conflict |
| Styles | Rule-based engines, each a trial | Five sleeves: opening range breakout, volatility breakout, trend swing, mean-reversion scalp, macro "go big" | No conflict; each sleeve is a trial |
| Where the AI runs | ONNX decision model loaded inside the EA; LLM advisor called by WebRequest | A Python "brain" (LightGBM quant model, LLM analyst, allocator) talking to a thin EA over a local socket | Yes |
| Sizing by AI | The AI moves size between zero and a fixed cap and can never exceed it | 1% risk per trade by default, raised to at most 2.5% in "go big" mode when both AI layers agree | Yes |
| Loss limits | Daily and total loss limits are inputs | 3% daily stop, 10% weekly stop, kill switch at 20% drawdown | No conflict; these are candidate defaults |
| Data | OANDA mid prices, CFTC, event calendar | Adds paid feeds for stocks, news, fundamentals and a calendar: about $150 a month lean, $420 full | Yes: spending |
| Who uses it | One trader, own terminal | Asked as an open question: own capital first, or a product later | Yes |
| Broker | None named | Coinexx for demo; Windows VPS near the broker | Yes |
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

### Benchmark and blueprint (Mythos, second account)

Full text is in `docs/prior/benchmark-and-blueprint.md`. It contains no backtest; every strategy in it is a proposal.

- Most 600% to 900% "growth" figures on mql5.com come from tiny accounts with deposits and withdrawals, grid or martingale bots, or backtests. Nearly all the leaders trade only gold. The no-grid systems with live data show 7% to 26% in a good month with drawdowns of 3% to 30%. Several of its figures come from a competing seller's blog and are marked as such.
- It proposes five sleeves. Two overlap with families the Keel session already rejected on design data: "volatility breakout" (Keel: volatility breakout from the day's open, no edge) and "trend swing" (Keel: daily breakout trend-following on gold and on 13 markets, profit factor 1.00 to 1.06). A trial on either needs to say what is different.
- Its "macro go big" sleeve depends on an LLM reading news and fundamentals. The document itself notes that this cannot be backtested without news timestamped to the second.
- Its four questions to the trader (drawdown cap, own capital or product, data tier, a repository) have not been answered as far as this file knows.

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

The research brief says to stop and report on a mismatch like this. It has been reported to the trader; no decision has come back. Three readings have now been tried against a target that is itself an out-of-sample number. Trying more until one fits would be tuning on out-of-sample data, so the next move is the trader's.

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
- Neither earlier expert advisor (`KeelXAU.mq5`, `GoldRangeNY.mq5`) is in this repo. Both are uncompiled. The trader has them in other accounts.
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
- Files are fetched with plain HTTPS from `https://huggingface.co/datasets/bunqi/<repo>/resolve/main/<path>`, which redirects to `us.aws.cdn.hf.co`.
- `python research/download.py D,60,5 XAUUSD,SPX500USD` fetches with 16 threads, checks every chunk's row count against its `.pod` sidecar, and writes one parquet per market and timeframe (for example `XAUUSD_5.parquet`) to the folder named by `MT5_DATA` (default `~/mt5_data`). It exits with status 1 on any failure. Symbols are the OANDA codes in the dataset names. Eight markets at three timeframes took about a minute.
- `python research/make_design.py FULL_FOLDER DESIGN_FOLDER` writes the design-only copy: every bar before 00:00 server time on 1 Jan 2018.
- With `MT5_DESIGN_ONLY=1` set, `research/common.py` refuses to load a file that contains later bars. Frozen runs read the full folder, so that ATR and moving averages have their warm-up, and report from 2018 onward.
- `research/out/` and `research/out_gold_trend.parquet` hold the Step 0 trade lists, including trades after 2017. That is by design for the three known engines, whose targets are out-of-sample figures. No other out-of-sample result exists anywhere in the repo.
- Fetched in the earlier session, in a cloud container that no longer exists (rerun the script): daily, hourly and 5-minute for XAUUSD, SPX500USD, NAS100USD, US30USD, DE30EUR, AUDNZD, AUDCAD, NZDCAD; daily and hourly for 42 more FX, metal, energy, bond and index symbols. No 1-minute data.
- CFTC history files (for example `https://www.cftc.gov/files/dea/history/fut_fin_txt_2020.zip`) return 200 with a browser User-Agent and 403 without one.
- FRED (`https://fred.stlouisfed.org/graph/fredgraph.csv?id=DFF`) was reachable, for financing rates.
