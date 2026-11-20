"""Download bunqi/OANDA_* parquet chunks and consolidate to one parquet per symbol/timeframe.
usage: download.py TF1,TF2 SYM1,SYM2   (SYM = OANDA instrument prefix e.g. XAUUSD)"""
import sys, io, os, requests, pandas as pd
from concurrent.futures import ThreadPoolExecutor
from huggingface_hub import HfApi
OUT = '/home/user/data'
api = HfApi()
allds = {d.id.split('/')[1].split('_')[1]: d.id for d in api.list_datasets(author='bunqi')}
s = requests.Session()
def get(url):
    for k in range(5):
        try:
            r = s.get(url, timeout=120); r.raise_for_status(); return r.content
        except Exception as e:
            err = e
    raise err
def one(sym, tf):
    out = f'{OUT}/{sym}_{tf}.parquet'
    if os.path.exists(out): return sym, tf, 'cached'
    rid = allds[sym]
    files = sorted(f.path for f in api.list_repo_tree(rid, tf, repo_type='dataset') if f.path.endswith('.parquet'))
    with ThreadPoolExecutor(16) as ex:
        blobs = list(ex.map(lambda p: get(f'https://huggingface.co/datasets/{rid}/resolve/main/{p}'), files))
    df = pd.concat([pd.read_parquet(io.BytesIO(b)) for b in blobs]).drop_duplicates('time').sort_values('time').reset_index(drop=True)
    df.to_parquet(out)
    return sym, tf, len(files), len(df)
if __name__ == '__main__':
    tfs = sys.argv[1].split(','); syms = sys.argv[2].split(',')
    for sym in syms:
        for tf in tfs:
            try: print(one(sym, tf), flush=True)
            except Exception as e: print(sym, tf, 'FAIL', repr(e)[:200], flush=True)
