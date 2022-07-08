# Simple wallet service

Simple REST-based wallet service. Requires two-way TLS authentication.
To run, client and server certificates must be present:

```
gunicorn --bind :8181 --keyfile server.key --certfile server.crt \
    --ca-certs client.crt --ssl-version TLSv1_2 --cert-reqs 2 \
    wallet.run:app
```

Then, to access, use client certificate and key files:

```
curl -vk --key client.key -E client.crt  https://localhost:8181/api/v1/key/
```

Or from python:
```
requests.post("https://localhost:8181/api/v1/key", data="{}", cert=("client.crt", "client.key"), verify=False)
```

(adjust the verify parameter if you don't use self-signed certificates).
