"""Build the design-only copy of the data: every bar that opens before 00:00 server time on 1 Jan 2018.

usage: python make_design.py FULL_FOLDER DESIGN_FOLDER
Researchers then work with MT5_DATA=DESIGN_FOLDER and MT5_DESIGN_ONLY=1. Frozen runs use FULL_FOLDER, so that
indicators have their warm-up, and report results from 2018 onward."""
import sys, os, glob, pandas as pd
SEAL_UTC = 1514757600      # 2017-12-31 22:00 UTC
if __name__ == '__main__':
    if len(sys.argv) != 3: sys.exit(__doc__)
    src, dst = sys.argv[1], sys.argv[2]; os.makedirs(dst, exist_ok=True)
    for f in sorted(glob.glob(f'{src}/*.parquet')):
        d = pd.read_parquet(f); k = d[d.time < SEAL_UTC]
        k.to_parquet(f'{dst}/{os.path.basename(f)}')
        print(os.path.basename(f), len(d), '->', len(k))
