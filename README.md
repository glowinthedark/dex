# DEXONLINE HTML data, cleaned up SQL Dump for SQLite

### External sources
- mariadb database dump: https://dexonline.ro/static/download/dex-database.sql.gz
- php backend https://github.com/dexonline/dexonline

### Importing the SQL dump into a SQLite database

Run from terminal:

```bash
sqlite3 DEX.db < dex.sql
```
