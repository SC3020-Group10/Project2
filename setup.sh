username=$1
password=$2
port=5432
database=TPC-H
host=localhost
rm .env
python -m pip install -r requirements.txt
echo -e "DATABASE=\"${database}\"\nUSER=\"${username}\"\nPASSWORD=\"${password}\"\nHOST=\"${host}\"\nPORT=\"${port}\"" >> .env
export PGPASSWORD=${password}
psql -U ${username} -c "DROP DATABASE IF EXISTS \"${database}\";"
psql -U ${username} -c "CREATE DATABASE \"${database}\";"
psql -h ${host} -d ${database} -U ${username} -p ${port} -a -w -f ./tables/create_region.sql
psql -h ${host} -d ${database} -U ${username} -p ${port} -a -w -f ./tables/create_nation.sql
psql -h ${host} -d ${database} -U ${username} -p ${port} -a -w -f ./tables/create_part.sql
psql -h ${host} -d ${database} -U ${username} -p ${port} -a -w -f ./tables/create_supplier.sql
psql -h ${host} -d ${database} -U ${username} -p ${port} -a -w -f ./tables/create_partsupp.sql
psql -h ${host} -d ${database} -U ${username} -p ${port} -a -w -f ./tables/create_customer.sql
psql -h ${host} -d ${database} -U ${username} -p ${port} -a -w -f ./tables/create_orders.sql
psql -h ${host} -d ${database} -U ${username} -p ${port} -a -w -f ./tables/create_lineitem.sql