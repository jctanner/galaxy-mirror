Galaxy Mirror or Proxy
----------------------

This is 2 implementations of a caching proxy for galaxy.ansible.com. One is written in python and one is written in golang.

Both are functionally the same, but cater to different audiences due to the language choices.


Python
------

1. cd python
2. docker build -t galaxy-mirror:latest .
3. docker run galaxy-mirror:latest

The container will listen on port 80 for incoming requests and will either forward the request off to galaxy.ansible.com or return the previously cached response from disk.

Each cached response will live in the /data directory on the container.


Golang
------

1. cd python
2. docker build -t galaxy-proxy:latest .
3. docker run galaxy-proxy:latest

The container will listen on port 80 for incoming requests and will either forward the request off to galaxy.ansible.com or return the previously cached response from disk.

Each cached response will live in the /app/.cache directory on the container.



Clients
-------

ansible-galaxy can either accept the -s argument for the server url, or it can read from ansible.cfg.

```
[jtanner@p1 golang]$ ansible-galaxy role install -s http://172.17.0.2/api/ geerlingguy.docker
Starting galaxy role install process
- downloading role 'docker', owned by geerlingguy
- downloading role from https://github.com/geerlingguy/ansible-role-docker/archive/6.0.4.tar.gz
- extracting geerlingguy.docker to /home/jtanner/.ansible/roles/geerlingguy.docker
- geerlingguy.docker (6.0.4) was installed successfully
```
