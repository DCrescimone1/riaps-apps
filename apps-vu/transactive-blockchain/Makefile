include /etc/lsb-release

setup:
	sudo apt-get install -y tmux
	sudo pip3 install python-dotenv
	sudo apt-get install -y libcurl4-openssl-dev
	sudo pip3 install pycurl
	sudo pip3 install influxdb
	sudo timedatectl set-timezone UTC
	make geth
	make grafana
	make influx
	pip3 install scipy



grafana:
	echo deb https://packages.grafana.com/oss/deb stable main | sudo tee /etc/apt/sources.list.d/grafana.list
	curl https://packages.grafana.com/gpg.key | sudo apt-key add -
	sudo apt-get update
	sudo apt-get install -y grafana
	sudo systemctl daemon-reload
	sudo systemctl start grafana-server
	sudo systemctl enable grafana-server.service

geth:
	wget https://gethstore.blob.core.windows.net/builds/geth-linux-amd64-1.7.0-6c6c7b2a.tar.gz
	tar -xvf geth-linux-amd64-1.7.0-6c6c7b2a.tar.gz
	mv geth-linux-amd64-1.7.0-6c6c7b2a ~/projects/
	rm -r geth*

influx:
	curl -sL https://repos.influxdata.com/influxdb.key | sudo apt-key add -
	echo "deb https://repos.influxdata.com/ubuntu ${DISTRIB_CODENAME} stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
	sudo apt-get update && sudo apt-get install -y influxdb
	sudo systemctl unmask influxdb.service
	sudo systemctl start influxdb
