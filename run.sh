#!/bin/bash
sudo iptables -I INPUT 1 -p tcp --dport 8082 -j ACCEPT
sudo iptables -I INPUT 1 -p tcp --dport 3000 -j ACCEPT
sudo iptables -I INPUT 1 -p tcp --dport 9090 -j ACCEPT
sudo iptables -I INPUT 1 -p tcp --dport 9100 -j ACCEPT
sudo iptables -I INPUT 1 -p tcp --dport 8089 -j ACCEPT
sudo ssh -L 9092:localhost:9092 tunnel@128.2.204.215 -NTf

