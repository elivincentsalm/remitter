#!/usr/bin/env bash

CA_NAME="mtls_ca"
mkdir certs && cd certs
openssl req -x509 -newkey rsa:4096 -keyout ca.key -out ca.crt -nodes -days 365 -subj "/CN=$CA_NAME/O=Client\ Certificate\ Demo"
openssl x509 -in ca.crt -text -noout
openssl req -newkey rsa:4096 -keyout server.key -out server.csr -nodes -days 365 -subj "/CN=44.203.68.40"
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -days 365 -out server.crt
openssl x509 -in server.crt -text -noout
openssl req -newkey rsa:4096 -keyout client.key -out client.csr -nodes -days 365 -subj "/CN=client"
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -days 365 -out client.crt
openssl x509 -in client.crt -text -noout
