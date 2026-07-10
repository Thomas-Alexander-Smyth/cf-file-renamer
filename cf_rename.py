"""
cf_rename.py - Rename Codeforces / CPH generated files so their name
includes BOTH the problem code and the problem title.
 
Examples of what it turns:
    1849A.cpp                 ->  1849A_Christmas_Angels.cpp
    1877D.py                  ->  1877D_Row_of_Effect.py
 
Usage:
    python cf_rename.py <code>              # rename files matching one code, in current dir
    python cf_rename.py <code> <folder>     # ...in a specific folder
    python cf_rename.py --all               # rename every matching file in current dir
    python cf_rename.py --all <folder>      # ...in a specific folder
    add --dry-run to any command to preview without touching files
 
<code> can be like: 1849A, 1849a, 1877D2, etc.
"""

import sys
import re
import json
import time
import urllib.request
from pathlib import Path

CACHE_FILE = Path.home() / '.cf_problems_cache.json'
CACHE_TTL = 60 * 60 * 23
API_URL = 'https://codeforces.com/api/problemset.problems'

def fetch_problemset():
    if CACHE_FILE.exists():
        age = time.time() - CACHE_FILE.stat().st_mtime

        if age < CACHE_TTL:
            with open(CACHE_FILE, 'r', encoding='utf-8') as file:
                return json.load(file)
    
    req = urllib.request.Request(API_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode('utf-8'))

    if data.get('status') != 'OK':
        raise RuntimeError(f'CF API Error {data}')
    
    lookup = {}
    for p in data['result']['problems']:
        code = f"{p['contestId']}{p['index']}"
        lookup[code] = p['name']

    with open(CACHE_FILE, 'w', encoding='utf-8') as file:
        json.dump(lookup, file)

    return lookup

def sanitize(name: str) -> str:
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'\s+', '_', name.strip())
    return name

def parse_code(s: str):
    m = re.search(r'(\d{1,4})\s*([A-Za-z]\d?)', s)
    if not m:
        return None
    return f'{m.group(1)}{m.group(2).upper()}'

def rename_file(path: Path, lookup: dict, dry_run = False):
    code = parse_code(path.stem)

    if not code or code not in lookup:
        return None

    title = sanitize(lookup[code])
    if title.lower() in path.stem.lower():
        return None
    
    new_stem = f'{code}_{title}'
    new_path = path.with_name(new_stem + path.suffix)

    if new_path.exists():
        print(f'Target already exists, skipped: {new_path.name}')
        return None
    
    if dry_run:
        print(f'[dry-run] {path.name}  ->  {new_path.name}')
        return new_path
    
    path.rename(new_path)
    print(f'Renamed: {path.name}  ->  {new_path.name}')
    return new_path

def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    dry_run = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]

    if args[0] == "--all":
        directory = Path(args[1]) if len(args) > 1 else Path(".")
        lookup = fetch_problemset()
        found = False
        for path in sorted(directory.iterdir()):
            if path.is_file():
                if rename_file(path, lookup, dry_run):
                    found = True
        if not found:
            print(f"No matching CF-named files found in {directory}")
        return
    
    code = parse_code(args[0])
    directory = Path(args[1]) if len(args) > 1 else Path(".")
    if not code:
        print(f"Could not parse a problem code from '{args[0]}'")
        sys.exit(1)
 
    lookup = fetch_problemset()
    if code not in lookup:
        print(f"Problem code {code} not found in the CF problemset.")
        sys.exit(1)
 
    print(f"{code}: {lookup[code]}")
 
    matched = False
    for path in sorted(directory.iterdir()):
        if path.is_file() and parse_code(path.stem) == code:
            rename_file(path, lookup, dry_run)
            matched = True
 
    if not matched:
        print(f"No files found matching code {code} in {directory}")
 
if __name__ == "__main__":
    main()