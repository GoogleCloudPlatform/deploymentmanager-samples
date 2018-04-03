#!/bin/bash

sudo apt-get update
sudo apt-get -y install default-jdk
sudo apt-get -y install git-core
DIR=spring-boot-cities-service
if [ ! -d "$DIR" ]; then
  git clone https://github.com/Sufyaan-Kazi/spring-boot-cities-service.git
fi
cd $DIR
nohup ./gradlew bootRun
