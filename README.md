# DEXONLINE HTML data, cleaned up SQL Dump for SQLite

### External sources
- mariadb database dump: https://dexonline.ro/static/download/dex-database.sql.gz
- php backend https://github.com/dexonline/dexonline

### Unpacking and importing the SQL dump into a SQLite database

Run from terminal:

```bash

# unpack the tgz file:
tar xzvf dexonline.sql.tgz

# create an SQLite database from the dump
sqlite3 DEX.db < dex.sql
```
