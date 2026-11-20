"""Step 0.3 Capped averaging (fade 2 ATR stretch from 100h mean), hourly bars."""
import numpy as np, pandas as pd
from common import *
def run(sym, mult=1.0, k_in=2.0, step=1.0, levels=4, grow=1.5, tp=0.5, hard=4.0, ma=100, entry_close=False, float_atr=False):
    H = load(sym, '60'); D = daily(sym)
    H['atr'] = H.sd.map(D.atr); H['ma'] = H.close.rolling(ma).mean()
    o, h, l, c, atr, mav = [H[k].values for k in ['open', 'high', 'low', 'close', 'atr', 'ma']]; st = H.st.values
    n = len(H); pos = False; baskets = []; eq = np.zeros(n); real = 0.0   # eq: realized + open P&L in R units at each bar close
    p = PIP(sym); rt, slip = cost(sym, None, mult)
    for i in range(ma, n - 1):
        eq[i] = real
        if not pos:
            if not np.isfinite(atr[i]) or not np.isfinite(mav[i]): continue
            z = (c[i] - mav[i]) / atr[i]
            if abs(z) >= k_in:
                s = -1 if z > 0 else 1; A = atr[i]; e0 = c[i] if entry_close else o[i + 1]; pos = True; i0 = i + 1    # signal on close, fill next open
                fills = [(e0, 1.0)]; nl = 1; sl = e0 - s * hard * A
                # worst case loss if all levels fill and the hard stop hits = basket risk (1R)
                lv = [e0 - s * step * A * k for k in range(levels)]; sz = [grow ** k for k in range(levels)]
                risk = sum(q * abs(x - sl) for x, q in zip(lv, sz)); lastmark = e0; units = 1.0; realized = 0.0
            eq[i] = real; continue
        if i < i0: eq[i] = real; continue
        # inside bar i (i >= i0): adds first (adverse), then stop, then target -- conservative ordering
        ex = None
        if float_atr and np.isfinite(atr[i]) and atr[i] != A:
            A = atr[i]; sl = e0 - s * hard * A; lv = [e0 - s * step * A * k for k in range(levels)]
        adv_ext = l[i] if s == 1 else h[i]; fav_ext = h[i] if s == 1 else l[i]
        added = False
        while nl < levels and s * (adv_ext - lv[nl]) <= 0:
            added = True
            px = lv[nl] if s * (o[i] - lv[nl]) > 0 else o[i]      # gap through -> fill at open
            fills.append((px, sz[nl])); nl += 1
        tot = sum(q for _, q in fills); avg = sum(x * q for x, q in fills) / tot
        if s * (adv_ext - sl) <= 0:
            ex = (sl if s * (o[i] - sl) > 0 else o[i]) - s * slip; why = 'stop'
        else:
            tgt = avg + s * tp * A
            if added:                                  # add and target in one bar: order unknown -> only exit if the CLOSE is beyond target
                if s * (c[i] - tgt) >= 0: ex = c[i]; why = 'tp'
            elif s * (fav_ext - tgt) >= 0:
                ex = tgt if s * (o[i] - tgt) < 0 else o[i]; why = 'tp'
        if ex is not None:
            pnl = sum(q * (s * (ex - x) - rt) for x, q in fills)
            baskets.append(dict(date=H.sd.values[i0], t_in=st[i0], t_out=st[i], side=s, atr=A, nlev=nl, avg=avg, exit=ex, why=why, risk=risk, R=pnl / risk, e0=e0, sym=sym))
            pos = False; real += pnl / risk; eq[i] = real
        else:
            eq[i] = real + sum(q * s * (c[i] - x) for x, q in fills) / risk
    eq[n - 1] = eq[n - 2]
    dp = pd.Series(eq, H.sd.values).groupby(level=0).last().diff().fillna(0)
    return pd.DataFrame(baskets), dp
if __name__ == '__main__':
    al = []; dps = {}
    for sym in ['AUDNZD', 'AUDCAD', 'NZDCAD']:
        b, dp = run(sym); al.append(b); dps[sym] = dp; d, o = split(b)
        print(sym, 'design', tstats(d), (d.why == 'stop').sum(), '| since2018', tstats(o), 'stops', (o.why == 'stop').sum(), o.nlev.value_counts().sort_index().to_dict(), 'sh', round(sharpe(dp[dp.index >= DESIGN_END]), 2))
    b = pd.concat(al); b.to_parquet(f'{ROOT}/out/avg_baskets.parquet'); d, o = split(b)
    P = pd.DataFrame(dps).fillna(0); P.to_parquet(f'{ROOT}/out/avg_daily.parquet'); tot = P.sum(axis=1)
    print('ALL design', tstats(d), (d.why == 'stop').sum(), 'sharpe', round(sharpe(tot[(tot.index >= START) & (tot.index < DESIGN_END)]), 2),
          '| since2018', tstats(o), 'stops', (o.why == 'stop').sum(), 'sharpe MTM', round(sharpe(tot[tot.index >= DESIGN_END]), 2))
    d2 = pd.concat([run(s_, 2.0)[0] for s_ in ['AUDNZD', 'AUDCAD', 'NZDCAD']]); print('2x cost design', tstats(split(d2)[0]))
    print(b[b.why == 'stop'][['sym', 't_in', 't_out', 'R']])
