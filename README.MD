On the docker host:
```
ip link set <interface> promisc on
sudo sysctl net.ipv4.conf.all.forwarding=1
sudo iptables -P FORWARD ACCEPT
docker network create -d macvlan --subnet=192.168.1.0/24 --gateway=192.168.1.1 --ip-range=192.168.1.224/27 --aux-address 'host=192.168.1.224' -o parent=<interface> my_net

# For connecting host to macvlan
sudo ip link add host_to_macvlan link eth0 type macvlan mode bridge
sudo ip addr add 192.168.1.224/27 dev host_to_macvlan
```

# TODO
- remove janus and add go2rtc
- the script that collects alarms from the camera doesn't restart when camera goes offline
