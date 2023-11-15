@echo off
set username=%1
set password=%2
set port=5432
set database=TPC-H
set host=localhost

if exist .env del .env
python -m pip install -r requirements.txt

echo DATABASE="%database%">>.env
echo USER="%username%">>.env
echo PASSWORD="%password%">>.env
echo HOST="%host%">>.env
echo PORT="%port%">>.env

set PGPASSWORD=%password%

psql -U %username% -c "DROP DATABASE IF EXISTS ""%database%"";"
psql -U %username% -c "CREATE DATABASE ""%database%"";"

psql -h %host% -d %database% -U %username% -p %port% -a -w -f ./tables/create_region.sql
psql -h %host% -d %database% -U %username% -p %port% -a -w -f ./tables/create_nation.sql
psql -h %host% -d %database% -U %username% -p %port% -a -w -f ./tables/create_part.sql
psql -h %host% -d %database% -U %username% -p %port% -a -w -f ./tables/create_supplier.sql
psql -h %host% -d %database% -U %username% -p %port% -a -w -f ./tables/create_partsupp.sql
psql -h %host% -d %database% -U %username% -p %port% -a -w -f ./tables/create_customer.sql
psql -h %host% -d %database% -U %username% -p %port% -a -w -f ./tables/create_orders.sql
psql -h %host% -d %database% -U %username% -p %port% -a -w -f ./tables/create_lineitem.sql