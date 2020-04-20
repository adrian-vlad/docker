On the docker host:
```
ip link set <interface> promisc on
sudo sysctl net.ipv4.conf.all.forwarding=1
sudo iptables -P FORWARD ACCEPT
docker network create -d macvlan --subnet=192.168.1.0/24 --gateway=192.168.1.1 --ip-range=192.168.1.16/29 -o parent=<interface> my_net
```