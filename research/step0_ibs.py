"""Step 0.2 Oversold close (IBS), long only. Daily P&L marked to market, unit = fraction of notional."""
import numpy as np, pandas as pd
from common import *
def run(sym, mult=1.0, lo=0.2, hi=0.8, maxd=5, stopk=3.0):
    D = daily(sym).dropna(); o, h, l, c, atr = [D[k].values for k in ['open', 'high', 'low', 'close', 'atr']]
    ibs = (c - l) / np.where(h > l, h - l, np.nan)
    n = len(D); pnl = np.zeros(n); trades = []; pos = False
    for i in range(1, n):
        if pos:
            held += 1; ex = None
            if o[i] <= sl: ex = o[i] - slip; why = 'gapstop'
            elif l[i] <= sl: ex = sl - slip; why = 'stop'
            elif ibs[i] > hi or c[i] > h[i - 1] or held >= maxd: ex = c[i]; why = 'rule'
            if ex is None: pnl[i] += (c[i] - c[i - 1]) / e0
            else:
                pnl[i] += (ex - c[i - 1] - rt) / e0; pos = False
                trades.append(dict(date=D.index[ie], t_out=D.index[i], entry=e0, exit=ex, stopdist=R, why=why, held=held, cost=rt, R=(ex - e0 - rt) / R, ret=(ex - e0 - rt) / e0))
                continue                         # no same-bar re-entry check below would be fine too; keep: can re-enter at this close
        if not pos and ibs[i] < lo and np.isfinite(atr[i]):
            # ATR for the stop: Wilder ATR(20) through the PRIOR day (known before today's close)
            pos = True; e0 = c[i]; ie = i; held = 0; R = stopk * atr[i]; sl = e0 - R; rt, slip = cost(sym, e0, mult)
    return pd.Series(pnl, D.index), pd.DataFrame(trades)
if __name__ == '__main__':
    for sym in ['SPX500USD', 'US30USD']:
        p, tr = run(sym); p.to_frame('pnl').to_parquet(f'{ROOT}/out/ibs_{sym}.parquet'); tr.to_parquet(f'{ROOT}/out/ibs_{sym}_trades.parquet')
        d, o = split(tr); p2, tr2 = run(sym, 2.0)
        print(sym, 'design', tstats(d), 'sharpe', round(sharpe(p[(p.index >= START) & (p.index < DESIGN_END)]), 2),
              '| since2018', tstats(o), 'sharpe', round(sharpe(p[p.index >= DESIGN_END]), 2), '| 2x design t', tstats(split(tr2)[0])['t'], tr.why.value_counts().to_dict())
