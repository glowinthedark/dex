#!/usr/bin/env python3

import pprint
import re
import sqlite3
import sys
from pathlib import Path

import mariadb

try:
    conn: mariadb.connection = mariadb.connect(
        user="root",
        password="dexonline",
        host="localhost",
        port=3306,
        database="dexonline"

    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

cur_maria: mariadb.connection.cursor = conn.cursor()


cur_maria.execute("""
    SELECT s.shortName, e.description, d.lexicon, d.internalRep
    FROM Entry e
    INNER JOIN EntryDefinition f ON e.id = f.entryId
    INNER JOIN Definition d ON d.id = f.definitionId 
    INNER JOIN Source s ON d.sourceId = s.id
""")

target_db_path = Path("dex.db")

target_db_path.unlink(missing_ok=True)

replacement_map = {
    re.compile('@'): ['\n<b>', '</b>'],
    re.compile(r'\$'): ['\n<i>', '</i>'],
    re.compile('#'): ['\n<span class="g">', '</span>'],
    re.compile('%'): ['\n<span class="b">', '</span>'],
}

tracker = {}


def re_replacer(match, rep):
    if match in tracker:
        tracker[match] = not tracker[match]
    else:
        tracker[match] = False

    prepend = ''
    # if match == '@' and tracker[match] is False:
    #     prepend = '<br>'

    return prepend + rep[tracker[match] and 1 or 0]


def drop_char_at(i, s):
    return s[:i] + s[i+1:]


count_unmatched = 0
unmatched_map = {}

with sqlite3.connect(target_db_path) as conn2:
    cursor2 = conn2.cursor()
    cursor2.execute(f"""CREATE TABLE IF NOT EXISTS word (
        id integer PRIMARY KEY autoincrement,
        w text,
        m text
         )""")

    for i, row in enumerate(cur_maria):
        sursa: str = row[0]
        headword_REAL: str = row[2]
        entry: str = row[3]
        # sursa_text: str = row[3]

        if entry.endswith('...') and len(entry) < 30:
            continue

        entry = re.sub("""{{\s*\^\{[\d\w]?\}Numerotarea\s+din\s+DLRM\s+este\s+diferită\s+de\s+cea\s+actuală,\s+la\s+vremea\s+respectivă\s+nefiind\s+luate\s+în\s+considerație\s+literele[^}]+}}""",
                       "", entry)

        entry = entry.replace('##', '#')
        entry = entry.replace('$$', '$')
        entry = entry.replace('@@', '@')
        entry = entry.replace('%%', '%')
        entry = entry.replace('\\', '')
        # entry = entry.replace('\\.', '.')
        # entry = entry.replace("\\'", "'")
        entry = entry.replace(r'{{', '<span class="foot">(')
        entry = entry.replace(r'}}', ')</span>')

        if '@' in entry:
            position_dollar = [m.start() for m in re.finditer(r'\$', entry)]
            position_amp = [m.start() for m in re.finditer('@', entry)]

            if len(position_dollar) > 1 and len(position_amp) > 1 and position_dollar[0] < position_amp[1]:
                # remove BOTH dollar signs
                entry = drop_char_at(position_dollar[0], entry)
                entry = drop_char_at(position_dollar[1] - 1, entry)

            # !!MUST recalculate once again!
            position_amp = [m.start() for m in re.finditer('@', entry)]
            position_hash = [m.start() for m in re.finditer('#', entry)]

            if len(position_hash) > 1 and len(position_amp) > 1 and position_hash[0] < position_amp[1]:
                # remove BOTH dollar signs
                entry = drop_char_at(position_hash[0], entry)
                entry = drop_char_at(position_hash[1] - 1, entry)

        for c in '@$#%':
            cnt = entry.count(c)
            if cnt % 2 != 0:
                count_unmatched += 1
                unmatched_map[f'{headword}-{c}-{cnt}'] = entry
                if cnt == 1:
                    entry.replace(c, '')
                else:
                    # remove the last char
                    ii = entry.rfind(c)
                    entry = entry[:ii] + entry[ii + 1:]


        entry = entry.replace(r'$civíu$', '@civíu@') \
            .replace(r'$armán (armáne),$', '@armán (armáne),@') \
            .replace(r'@$argeá@ #sf#$', '@argeá@ #sf#') \
            .replace('"@W@"', '@W@') \
            .replace('(< ', '(') \
            .replace('[< ', '[') \
            .replace(' < ', '')
        entry = re.sub(r'^[*\d)]\s*', '', entry)
        entry = re.sub(r'^\*\s*@?', '@', entry)
        entry = re.sub(r'\^\{([-\[\]\w\d]+)\}', r'<sup>\1</sup>', entry)
        # entry = entry.replace(r'^{v}', '<sup>v</sup>')
        # entry = re.sub(r'^\$(\w+)\$*', r'\1', entry)

        if '^' in entry:
            entry = re.sub(r'\^\{?([\d\w]+)\}?', r'<sup>\1</sup>', entry)

        index_comma = entry.find(',')
        index_space = entry.find(' ')
        index_ampersand = entry.find('@')
        pos_norm = 0
        pos_fuzz = 0

        try:
            if '@' in entry:
                match_norm = re.search(r'@([^@]+[,. ]*)@', entry)
                if match_norm:
                    headword_norm = match_norm.group(1)
                    pos_norm = match_norm.end(1)

                match_by_separator = re.search(r'([^\s,.?!;:]+)[\s,.?!;:]', entry)

                if match_by_separator:
                    headword_fuzz = match_by_separator.group(1)
                    pos_fuzz = match_by_separator.end(1)

                if pos_norm != 0 or pos_fuzz != 0:
                    if pos_norm >= pos_fuzz:
                        headword = headword_norm
                        definition = entry[pos_norm + 1:].strip()
                    else:
                        headword = headword_fuzz
                        definition = entry[pos_fuzz + 1:].strip()

                else:
                    raise Exception("wtf?")
            else:
                definition = entry

        except Exception as e:
            print(str(e), entry)

            try:
                if ' ' in entry and ',' in entry:
                    if index_comma < index_space:
                        headword, definition = entry.split(',', 1)
                    else:
                        headword, definition = entry.split(' ', 1)
                else:
                    headword, definition = re.split(r'\W', entry, maxsplit=1)
            except Exception as e:
                print(str(e))

        definition = definition.strip()

        definition_current = definition

        for patt, replacements in replacement_map.items():
            tracker.clear()
            definition_current = patt.sub(lambda m: re_replacer(m.group(), replacements), definition_current)

        definition_current: str = definition_current.replace('**', '\n<span class="ex">◆</span>').strip()

        definition_current += f""" <abbr>{sursa}</abbr>"""

        cursor2.execute('''INSERT INTO word (w, m) values (?,?)''', [headword_REAL.lower(), definition_current])

        if i % 1000 == 0:
            print(f'{i} ENTRY:{headword_REAL} INTRNL:{headword}')

print(f'Wrote {target_db_path.absolute()}')
print(f'''Total count: {i}
Count unmatched: {count_unmatched}
''')
pprint.pprint(unmatched_map.keys())
