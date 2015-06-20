#!/bin/sh
# This script deletes the entire database, calls syncdb, and imports data tables

# Drop all tables in cascade
psql directoalartista << EOF
DROP SCHEMA public CASCADE;
CREATE SCHEMA "public" AUTHORIZATION "postgres";
CREATE EXTENSION unaccent;
ALTER FUNCTION unaccent(text) IMMUTABLE;
EOF

# Syncdb
python manage.py syncdb --noinput

# Creates an admin user with credentials
# - User: admin@directoalartista
# - Password: 1234
# and imports generic data
psql directoalartista << EOF
\i ./dbdumps/artistprofile_artistcategory;
\i ./dbdumps/artistprofile_artisteventtypecategory;
\i ./dbdumps/artistprofile_artistprovince;
EOF
