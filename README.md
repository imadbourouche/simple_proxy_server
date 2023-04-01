# simple_proxy_server
A forward proxy server that allows users to:

* Intercept HTTP requests and  forward responses
* Log HTTP requests
* Black list domains

## Run
* Python
```
python3 proxy.py -mc 10 -bs 8192
```

* Docker
```
docker build -f Dockerfile . -t proxy-server

docker run -p 1234:1234 -it proxy-server
```
