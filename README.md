# cf-file-renamer

A small command-line tool that renames Codeforces / CPH-generated solution files so their filename includes **both** the problem code and the problem title — instead of just one or the other.

```
3A.cpp    ->  3A_Shortest_path_of_the_king.cpp
13B.py    ->  13B_Letter_A.py
23C.cpp   ->  23C_Oranges_and_Apples.cpp
```

## Why

The [CPH (Competitive Programming Helper)](https://marketplace.visualstudio.com/items?itemName=DivyanshuAgrawal.competitive-programming-helper) VS Code extension names generated files either by problem code or by problem name — not both. This script fixes that by fetching the real problem title from the Codeforces API and combining it with the code.

## Requirements

- Python 3.6+
- No external packages — uses only the standard library (`urllib`, `json`, `re`, `pathlib`, etc.)

## Usage

```bash
# rename a single problem's file(s) in the current folder
python cf_rename.py 1849A

# ...in a specific folder
python cf_rename.py 1849A ./solutions

# rename every matching file in the current folder
python cf_rename.py --all

# ...in a specific folder
python cf_rename.py --all ./solutions

# preview changes without renaming anything
python cf_rename.py --all --dry-run
```

The `<code>` argument accepts problem codes like `1849A`, `1849a` (case-insensitive), or split-problem codes like `1213D2`.

## How it works

1. On first run, fetches the full Codeforces problem list from the public [`problemset.problems`](https://codeforces.com/api/problemset.problems) API and caches it locally (`~/.cf_problems_cache.json`) for 23 hours, so repeated runs don't hit the network every time.
2. Extracts a problem code from each filename using a regex.
3. Looks up the real problem title, sanitizes it into a filename-safe string (letters, digits, underscores, hyphens only), and renames the file to `<code>_<title><extension>`.
4. Skips files that are already correctly tagged, and skips renaming if a file with the target name already exists (never overwrites).

## Example

```
$ python cf_rename.py --all --dry-run
[dry-run] 3A.cpp   ->  3A_Shortest_path_of_the_king.cpp
[dry-run] 13B.py   ->  13B_Letter_A.py
[dry-run] 23C.cpp  ->  23C_Oranges_and_Apples.cpp

$ python cf_rename.py --all
Renamed: 3A.cpp   ->  3A_Shortest_path_of_the_king.cpp
Renamed: 13B.py   ->  13B_Letter_A.py
Renamed: 23C.cpp  ->  23C_Oranges_and_Apples.cpp
```

## Notes

- The local cache lives at `~/.cf_problems_cache.json`. Delete it manually if you ever want to force a refresh before the 23-hour TTL expires.
- The rename check is based on filename substring matching — running the script again on an already-renamed file is a no-op.