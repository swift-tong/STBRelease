#! /bin/bash

TOMCAT_HOME=/usr/local/apache-tomcat-8.5.24
WEBAPPS_HOME=$TOMCAT_HOME/webapps

unlink $WEBAPPS_HOME/stbrelease/data
unlink $WEBAPPS_HOME/stbrelease/js/stbrelease.cfg.json

cp /usr/local/stbrelease/stbrelease.war $WEBAPPS_HOME/.
echo "Please wait..."
sleep 10
rm -rf $WEBAPPS_HOME/stbrelease/data
rm -rf $WEBAPPS_HOME/stbrelease/js/stbrelease.cfg.json
ln -s /usr/local/stbrelease/data $WEBAPPS_HOME/stbrelease/data
ln -s /usr/local/stbrelease/scripts/stbrelease.cfg.json $WEBAPPS_HOME/stbrelease/js/stbrelease.cfg.json

echo "Done!"
