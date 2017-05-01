# PG & J
Postgres schema export to json

Basic Usage
-----------

```bash
virtualenv venv
pip install -r requirements-pypy.txt
bin/pgandj -u USERNAME --host HOSTNAME -p PORT -w "PASSWORD"  DATABASE
```

Sample Output
-----------


```json
{
    "alternate": {
        "fields": {
            "id": {
                "name": "id",
                "type": "integer",
                "nullable": false,
                "default": "nextval('alternate_id_seq'::regclass)",
                "references_foreign_key": null,
                "referenced_by_foreign_key": [
                    [
                        "variant",
                        "alternate_id"
                    ]
                ],
                "leads_index": true,
                "unique": true
            },
            "created": {
                "name": "created",
                "type": "timestamp with time zone",
                "nullable": false,
                "default": "now()",
                "references_foreign_key": null,
                "referenced_by_foreign_key": null,
                "leads_index": false
            },
            "element_id": {
                "name": "element_id",
                "type": "integer",
                "nullable": false,
                "default": null,
                "references_foreign_key": [
                    "element",
                    "id"
                ],
                "referenced_by_foreign_key": null,
                "leads_index": true
            },
            "owner_id": {
                "name": "owner_id",
                "type": "integer",
                "nullable": false,
                "default": null,
                "references_foreign_key": [
                    "person",
                    "id"
                ],
                "referenced_by_foreign_key": null,
                "leads_index": false
            },
            "shotgun_id": {
                "name": "shotgun_id",
                "type": "integer",
                "nullable": false,
                "default": null,
                "references_foreign_key": null,
                "referenced_by_foreign_key": null,
                "leads_index": false
            },
            "name": {
                "name": "name",
                "type": "character varying",
                "nullable": false,
                "default": null,
                "references_foreign_key": null,
                "referenced_by_foreign_key": null,
                "leads_index": false
            },
            "attributes": {
                "name": "attributes",
                "type": "jsonb",
                "nullable": true,
                "default": "'{}'::jsonb",
                "references_foreign_key": null,
                "referenced_by_foreign_key": null,
                "leads_index": false
            }
        },
        "indices": {
            "alternate_pkey": {
                "fields": [
                    "id"
                ],
                "unique": true
            },
            "uniquealternate": {
                "fields": [
                    "element_id",
                    "name"
                ],
                "unique": true
            }
        }
    }
}
```
