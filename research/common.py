"""Shared helpers: data loading, server clock, daily bars, Wilder ATR, costs, stats, trial log."""
import json, os, numpy as np, pandas as pd
DATA = os.environ.get('MT5_DATA', '/home/user/data')   # set MT5_DATA to the folder download.py wrote to
ROOT = os.path.dirname(os.path.abspath(__file__))
DESIGN_END = pd.Timestamp('2018-01-01')   # design: Apr 2006 .. Dec 2017 ; OOS: Jan 2018 .. Nov 2026
START = pd.Timestamp('2006-04-01')

def load(sym, tf):
    """Bars with server-clock timestamp 'st' (New York local time + 7h), bar OPEN time."""
    d = pd.read_parquet(f'{DATA}/{sym}_{tf}.parquet')
    ny = pd.to_datetime(d.time, unit='s', utc=True).dt.tz_convert('America/New_York').dt.tz_localize(None)
    d['st'] = ny + pd.Timedelta(hours=7)
    d = d[d.st.dt.dayofweek < 5].reset_index(drop=True)
    d['sd'] = d.st.dt.normalize()
    return d

def daily(sym, src='60'):
    """Daily bars built from intraday data; a day = server calendar day (rolls 17:00 New York)."""
    h = load(sym, src)
    g = h.groupby('sd')
    D = pd.DataFrame({'open': g.open.first(), 'high': g.high.max(), 'low': g.low.min(),
                      'close': g.close.last(), 'n': g.close.size()})
    D = D[D.n >= (4 if src == '60' else 40)]
    D['atr'] = wilder_atr(D, 20).shift(1)      # prior-day ATR: known at today's open
    return D

def wilder_atr(D, n=20):
    pc = D.close.shift(1)
    tr = np.maximum(D.high - D.low, np.maximum((D.high - pc).abs(), (D.low - pc).abs()))
    tr.iloc[0] = D.high.iloc[0] - D.low.iloc[0]
    return tr.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()

PIP = lambda s: 0.01 if s.endswith('JPY') else 0.0001
# round-trip cost and stop slippage in price units (top of the stated ranges for FX)
IDX = {'SPX500USD': (0.7, 0.25), 'NAS100USD': (2.0, 1.0), 'US30USD': (3.0, 2.0), 'DE30EUR': (2.0, 1.0)}
MAJ = {'EURUSD': 1.0, 'USDJPY': 1.0, 'GBPUSD': 1.5, 'AUDUSD': 1.5, 'USDCAD': 1.5, 'USDCHF': 1.5, 'NZDUSD': 1.5}
def cost(sym, price=None, mult=1.0):
    """(round trip, stop slippage) in price units. Slippage is not doubled in the 2x-cost test? -> it IS (mult applies to both)."""
    if sym == 'XAUUSD':
        return mult * max(0.35, 1e-4 * price), mult * 0.10
    if sym in IDX:
        return mult * IDX[sym][0], mult * IDX[sym][1]
    p = PIP(sym)
    if sym in MAJ:
        return mult * MAJ[sym] * p, mult * 0.2 * p
    return mult * 2.5 * p, mult * 0.2 * p     # crosses: top of 2.2-2.5 range

def tstat(x):
    x = np.asarray(x, float); x = x[~np.isnan(x)]
    return 0.0 if len(x) < 2 or x.std(ddof=1) == 0 else x.mean() / x.std(ddof=1) * np.sqrt(len(x))
def pf(x):
    x = np.asarray(x, float); l = -x[x < 0].sum()
    return np.inf if l == 0 else x[x > 0].sum() / l
def sharpe(daily_pnl):
    x = np.asarray(daily_pnl, float)
    return 0.0 if x.std() == 0 else x.mean() / x.std(ddof=1) * np.sqrt(252)
def tstats(tr, col='R'):
    """summary of a trades frame"""
    if len(tr) == 0: return dict(n=0, meanR=0, t=0, pf=0)
    return dict(n=int(len(tr)), meanR=round(float(tr[col].mean()), 4), t=round(float(tstat(tr[col])), 2), pf=round(float(pf(tr[col])), 2))
def split(tr, col='date'):
    d = tr[(tr[col] >= START) & (tr[col] < DESIGN_END)]; o = tr[tr[col] >= DESIGN_END]
    return d, o
def log_trial(rec):
    with open(f'{ROOT}/trials.jsonl', 'a') as f: f.write(json.dumps(rec, default=str) + '\n')
