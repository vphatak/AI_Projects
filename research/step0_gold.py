"""Step 0.1 Gold trend-day reproduction (also engine G1 run)."""
import sys, numpy as np, pandas as pd
from common import *
def run(mult=1.0, lo=1.2, hi=3.0, stop=0.6, hours=(16, 17, 18, 19), exit_min=22 * 60 + 55, sym='XAUUSD'):
    m = load(sym, '5'); D = daily(sym)
    m['mn'] = m.st.dt.hour * 60 + m.st.dt.minute
    out = []
    for sd, g in m.groupby('sd', sort=True):
        if sd not in D.index: continue
        atr = D.atr.get(sd); 
        if not np.isfinite(atr): continue
        o = g.open.values; h = g.high.values; l = g.low.values; c = g.close.values; mn = g.mn.values
        dopen = o[0]
        for hr in hours:
            i = np.searchsorted(mn, hr * 60)
            if i >= len(mn) or mn[i] != hr * 60: continue          # need the bar that opens exactly on the hour
            px = o[i]; dist = (px - dopen) / atr
            if lo <= abs(dist) <= hi:
                s = 1 if dist > 0 else -1
                rt, slip = cost(sym, px, mult); R = stop * atr; sl = px - s * R
                ex = None
                for j in range(i, len(mn)):
                    if mn[j] >= exit_min:                              # time exit at the open of the 22:55 bar
                        ex = o[j]; why = 'time'; break
                    if (s == 1 and o[j] <= sl) or (s == -1 and o[j] >= sl):
                        ex = o[j] - s * slip; why = 'gapstop'; break
                    if (s == 1 and l[j] <= sl) or (s == -1 and h[j] >= sl):
                        ex = sl - s * slip; why = 'stop'; break
                if ex is None: ex = c[-1]; why = 'eod'; j = len(mn) - 1
                out.append(dict(date=sd, t_in=g.st.values[i], t_out=g.st.values[j], side=s, entry=px, exit=ex, stopdist=R,
                                atr=atr, why=why, cost=rt, R=(s * (ex - px) - rt) / R))
                break                                                 # one trade a day
    return pd.DataFrame(out)
if __name__ == '__main__':
    tr = run(); tr.to_parquet(f'{ROOT}/out_gold_trend.parquet')
    d, o = split(tr)
    print('design', tstats(d)); print('since2018', tstats(o)); print('2x cost design', tstats(split(run(2.0))[0]))
    print(tr.why.value_counts().to_dict()); print(o.groupby(o.date.dt.year).R.agg(['size', 'mean']).round(3).T)
