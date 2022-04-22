# DEXONLINE HTML data, cleaned up SQL Dump for SQLite

### External sources
- mariadb database dump: https://dexonline.ro/static/download/dex-database.sql.gz
- php backend https://github.com/dexonline/dexonline

### macOS Dictionary.app bundle

1. Download [DEX for macOS Dictionary.app](https://mega.nz/file/DggFxDqZ#bhXEfZUJemFcQUTPHjePjYUFicnjwNZ46oQZfI2bCfA)
2. Unpack into `~/Library/Dictionaries`
3. Launch the Apple Dictionary.app and under Preferences (`⌘` + `,`) enable DEX. Optionally drag the DEX to the top of the list if you want to change the order of dictionaries.

### Unpacking and importing the SQL dump into a SQLite database

Run from terminal:

```bash

# unpack the tgz file:
tar xzvf dexonline.sql.tgz

# create an SQLite database from the dump
sqlite3 DEX.db < dex.sql
```
