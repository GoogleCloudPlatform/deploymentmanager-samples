############################################################
# Dockerfile to build MySQL container images               #
# Based on Ubuntu                                          #
############################################################

# Use Ubuntu as base image
FROM ubuntu

# Disable upstart because it doesn’t work with Docker
RUN dpkg-divert --local --rename --add /sbin/initctl
RUN ln -nfs /bin/true /sbin/initctl

# Make sure to update packages
RUN apt-get update
RUN apt-get upgrade -y

# Install MySQL
RUN apt-get -y install mysql-client mysql-server

# Update the bind-address
RUN sed -i -e"s/^bind-address\s*=\s*127.0.0.1/bind-address = 0.0.0.0/" /etc/mysql/my.cnf

# This is necessary to configure ports
RUN sed -i -e"s/^port\s*=\s*3306/port= 8080/" /etc/mysql/my.cnf

# Run a startup script to launch MySQL
ADD ./startup.sh /opt/startup.sh

EXPOSE 8080

CMD ["/bin/bash", "/opt/startup.sh"]
