#/bin/bash

if [ ! -f /var/lib/mysql/ibdata1 ]; then
    echo "Launching mysql_install_db"
    mysql_install_db
fi

echo "Launching mysql_safe"
/usr/bin/mysqld_safe &
echo "sleeping..."
sleep 10s

echo "Configuring the database"
echo "GRANT ALL ON *.* TO admin IDENTIFIED BY 'mypassword' WITH GRANT OPTION; FLUSH PRIVILEGES" | mysql --protocol=tcp --port=8080
echo "CREATE DATABASE demo;" | mysql --protocol=tcp --port=8080
echo "create table demo.log (message varchar(256), id mediumint auto_increment, primary key(id));" | mysql --protocol=tcp --port=8080

killall mysqld
sleep 10s

/usr/bin/mysqld_safe
