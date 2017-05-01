#!/usr/bin/env python

queries={}

queries["list_databases"] = """
SELECT
    datname
FROM
    pg_database
WHERE
    datistemplate = false"""

queries["list_tables"] = """
SELECT
    table_catalog,
    table_name
FROM
    information_schema.tables
WHERE
    table_schema='public'
AND
    table_type='BASE TABLE'
order by
    table_name
"""


queries["list_foreign_keys"] = """
SELECT
    tc.constraint_catalog as database_name,
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM
    information_schema.table_constraints AS tc,
    information_schema.key_column_usage AS kcu,
    information_schema.constraint_column_usage AS ccu
WHERE
    constraint_type = 'FOREIGN KEY' AND
    tc.constraint_name = kcu.constraint_name AND
    ccu.constraint_name = tc.constraint_name AND
    tc.table_name = %s
"""

queries["list_table_columns"] = """
SELECT
    table_catalog,
    table_name,
    column_name,
    column_default,
    -- character_maximum_length,
    -- numeric_precision,
    -- numeric_precision_radix,
    -- numeric_scale,
    data_type,
    is_nullable
FROM
    information_schema.columns
WHERE
    table_schema = 'public' AND
    table_name = %s
ORDER BY
    table_name,
    ordinal_position
"""

queries["list_table_indices"] = """
select
    t.relname as table_name,
    i.relname as index_name,
    ix.indisunique as unique,
    array_agg(a.attname) as column_names
from
    pg_class t,
    pg_class i,
    pg_index ix,
    pg_attribute a
where
    t.oid = ix.indrelid
    and i.oid = ix.indexrelid
    and a.attrelid = t.oid
    and a.attnum = ANY(ix.indkey)
    and t.relkind = 'r'
    and t.relname = %s
group by
    t.relname,
    i.relname,
    ix.indisunique
order by
    t.relname,
    i.relname;
"""

if __name__ == '__main__':
    import json
    fh = open("./output.json", "w")
    res = json.dump(queries, fh, indent=4)
    fh.close()
