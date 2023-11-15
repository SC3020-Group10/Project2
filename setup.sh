username=$1
password=$2
port=5432
database=TPC-H
host=localhost
rm .env
python -m pip install -r requirements.txt
echo -e "DATABASE=\"${database}\"\nUSER=\"${username}\"\nPASSWORD=\"${password}\"\nHOST=\"${host}\"\nPORT=\"${port}\"" >> .env
export PGPASSWORD=${password}
psql -U ${username} -c "CREATE DATABASE \"${database}\";"
psql -h ${host} -d ${database} -U ${username} -p ${port} -a -w -f ./tables/create_all.sql