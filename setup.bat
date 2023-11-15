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

psql -U %username% -c "CREATE DATABASE ""%database%"";"

psql -h %host% -d %database% -U %username% -p %port% -a -w -f ./tables/create_all.sql