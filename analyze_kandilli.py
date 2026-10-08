"""Usage: python analyze_kandilli.py path/to/koeri_export.csv
The export should have headers for date, latitude, longitude, depth, magnitude.
Creates statistics.txt, cleaned_earthquakes.csv, magnitude_histogram.png.
"""
import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

if len(sys.argv) != 2:
    raise SystemExit('Usage: python analyze_kandilli.py <KOERI CSV or TSV file>')
path = Path(sys.argv[1]); output = Path('results'); output.mkdir(exist_ok=True)
if not path.exists(): raise SystemExit(f'No file found: {path}')
# Detect commas, tabs, or semicolons. KOERI fixed-width text may need custom parser.
df = pd.read_csv(path, sep=None, engine='python', encoding='utf-8-sig')
original_count = len(df)
lookup = {str(c).strip().lower().replace(' ','').replace('_',''): c for c in df.columns}
alternatives = {
    'latitude':['latitude','lat','enlem'],
    'longitude':['longitude','lon','long','boylam'],
    'depth':['depth','depthkm','derinlik'],
    'magnitude':['magnitude','mag','ml','mw','md','buyukluk','büyüklük'],
    'date':['date','tarih','datetime','origin_time','origintime','timestamp'],
    'time':['time','saat']
}
cols = {name: next((lookup[key] for key in keys if key in lookup), None) for name,keys in alternatives.items()}
if any(cols[k] is None for k in ('latitude','longitude','depth','magnitude','date')):
    raise SystemExit(f'Columns found: {list(df.columns)}\nPlease rename columns to: date, latitude, longitude, depth, magnitude (optional time).')
selected = df.rename(columns={v:k for k,v in cols.items() if v is not None}).copy()
if 'time' in selected.columns and 'time' != 'date':
    selected['date'] = selected['date'].astype(str) + ' ' + selected['time'].astype(str)
selected['date'] = pd.to_datetime(selected['date'], errors='coerce', dayfirst=True)
for c in ('latitude','longitude','depth','magnitude'):
    selected[c] = pd.to_numeric(selected[c], errors='coerce')
fields = ['date','latitude','longitude','depth','magnitude']
missing = selected[fields].isna().sum()
duplicates = selected[fields].duplicated().sum()
clean = selected.dropna(subset=fields).drop_duplicates(subset=fields).copy()
clean = clean[clean.latitude.between(-90,90) & clean.longitude.between(-180,180) & (clean.depth>=0)]
report = [f'SOURCE FILE: {path.name}', f'ORIGINAL ROWS: {original_count}',
          f'RECORDS WITH FULL REQUIRED FIELDS, DEDUPLICATED: {len(clean)}',
          f'DUPLICATED RECORDS (on key fields): {duplicates}',
          'MISSING BY FIELD:', missing.to_string(),
          f'DATE RANGE: {clean.date.min()} to {clean.date.max()}',
          'DESCRIPTIVE STATISTICS:', clean[['latitude','longitude','depth','magnitude']].describe().to_string(),
          'EVENTS PER YEAR:', clean.groupby(clean.date.dt.year).size().to_string()]
(output/'statistics.txt').write_text('\n\n'.join(report), encoding='utf-8')
clean.to_csv(output/'cleaned_earthquakes.csv', index=False)
if len(clean):
    clean.magnitude.hist(bins=30); plt.xlabel('Magnitude (as exported)'); plt.ylabel('Event count'); plt.title('Magnitude distribution')
    plt.tight_layout(); plt.savefig(output/'magnitude_histogram.png', dpi=160)
print('\n\n'.join(report))
print('\nSaved outputs under ./results/')
