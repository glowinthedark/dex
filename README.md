# DEXONLINE HTML data, cleaned up SQL Dump for SQLite

### External sources used
- mariadb SQL database dump from the [dexonline](https://github.com/dexonline/dexonline) project: https://dexonline.ro/static/download/dex-database.sql.gz


### macOS Dictionary.app bundle

1. Download [DEX for macOS Dictionary.app](https://mega.nz/file/C0B0QDiA#FqvhFNHGmjKhYzCB5oUCLGE0sHL3zpbYwDuTMijX6BM)
2. Unpack into `~/Library/Dictionaries`
3. Launch the Apple **Dictionary.app** and under Preferences (`⌘` + `,`) enable DEX. Optionally, drag the DEX item to the top of the list if you want to change the order of dictionaries.

### Unpacking and importing the SQL dump into a SQLite database

Run from terminal:

```bash

# unpack the tgz file:
tar xzvf dexonline.sql.tgz

# create an SQLite database from the dump
sqlite3 DEX.db < dex.sql
```
