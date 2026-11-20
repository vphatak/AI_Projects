"""Download bunqi/OANDA_* parquet chunks, check them against their .pod sidecars, and write one parquet per
symbol and timeframe into the folder named by MT5_DATA (default ~/mt5_data; keep it outside the checkout).

usage: python download.py D,60,5 XAUUSD,SPX500USD,AUDNZD
Exits with status 1 if any symbol/timeframe failed or disagreed with its sidecars."""
import sys, io, os, json, requests, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from huggingface_hub import HfApi
OUT = os.environ.get('MT5_DATA', os.path.expanduser('~/mt5_data'))
api = HfApi(); s = requests.Session()
def get(url):
    for k in range(5):
        try:
            r = s.get(url, timeout=120); r.raise_for_status(); return r.content
        except Exception as e:
            err = e
    raise err
def one(sym, tf, allds):
    out = f'{OUT}/{sym}_{tf}.parquet'
    if os.path.exists(out): return f'{sym} {tf} already present (delete the file to refetch)'
    rid = allds[sym]; base = f'https://huggingface.co/datasets/{rid}/resolve/main/'
    tree = [f.path for f in api.list_repo_tree(rid, tf, repo_type='dataset')]
    files = sorted(p for p in tree if p.endswith('.parquet')); pods = sorted(p for p in tree if p.endswith('.pod'))
    with ThreadPoolExecutor(16) as ex:
        blobs = list(ex.map(lambda p: get(base + p), files)); podb = list(ex.map(lambda p: get(base + p), pods))
    parts = [pd.read_parquet(io.BytesIO(b)) for b in blobs]
    want = {json.loads(b)['parquet_file']: json.loads(b)['row_count'] for b in podb}
    bad = [p for p, d in zip(files, parts) if want.get(os.path.basename(p)) != len(d)]
    if bad or len(pods) != len(files):
        raise RuntimeError(f'{len(bad)} of {len(files)} chunks disagree with their .pod row counts ({len(pods)} sidecars), e.g. {bad[:2]}')
    raw = sum(len(d) for d in parts)
    df = pd.concat(parts).drop_duplicates('time').sort_values('time').reset_index(drop=True)
    df.to_parquet(out)
    return f'{sym} {tf} ok: {len(files)} chunks, {len(df)} bars ({raw - len(df)} duplicate timestamps dropped)'
if __name__ == '__main__':
    if len(sys.argv) != 3: sys.exit(__doc__)
    os.makedirs(OUT, exist_ok=True)
    allds = {d.id.split('/')[1].split('_')[1]: d.id for d in api.list_datasets(author='bunqi')}
    failed = 0
    for sym in sys.argv[2].split(','):
        for tf in sys.argv[1].split(','):
            try: print(one(sym, tf, allds), flush=True)
            except Exception as e: failed += 1; print(sym, tf, 'FAIL', repr(e)[:300], flush=True)
    sys.exit(1 if failed else 0)
