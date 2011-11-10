import os, sys
sys.path.insert(0, '../')
os.environ['DJANGO_SETTINGS_MODULE'] = 'euscanwww.settings'

from django import db

c = db.connection.cursor()
try:
    c.execute(r"""SELECT c.relname
        FROM pg_catalog.pg_class c
            LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relkind IN ('S','')
            AND n.nspname NOT IN ('pg_catalog', 'pg_toast')
            AND pg_catalog.pg_table_is_visible(c.oid)
        """)
    to_update = []
    for row in c:
        seq_name = row[0]
        rel_name = seq_name.split("_id_seq")[0]
        to_update.append((seq_name, rel_name,))
    for row in to_update:
        c.execute(r"SELECT setval('%s', max(id)) FROM %s"%row)
finally:
    c.close()
