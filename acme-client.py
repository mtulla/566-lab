#!/usr/bin/python3

import requests
import cryptography.hazmat.primitives.asymmetric.ec as ec
from cryptography.hazmat.primitives import serialization, hashes
import cryptography.hazmat.primitives.asymmetric.rsa as rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
from authlib.jose import jwt, JsonWebSignature, JsonWebKey
import base64
import re
from pathlib import Path

acme_dir_url = 'http://zoobar-ca.csail.mit.edu:5000/directory'
zoobar_hostname = 'zoobar-localhost.csail.mit.edu'
key_pn = 'tls.key'
cert_pn = 'tls.cert'

## Your job is to set up a TLS key and certificate for your Zoobar web server.
## The TLS key goes into key_pn, and the certificate goes into cert_pn.
## Use the ACME CA server at acme_dir_url to get a certificate for the
## server name specified in zoobar_hostname.

## The "zoobar-localhost.csail.mit.edu" name is treated specially by our CA:
## it uses port 8080 to send the challenge, instead of port 80.

# Generate keys.
private_key = ec.generate_private_key(ec.SECP256R1)
public_key = private_key.public_key()
public_key_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo) 
jwk = JsonWebKey.import_key(public_key_bytes)
tls_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)
with open(key_pn, "wb") as f:
    f.write(tls_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ))

# Get the directory URLs.
dir_urls = requests.get(acme_dir_url).json()

# Get a new nonce.
nonce = requests.head(dir_urls['newNonce']).headers["Replay-Nonce"]

# Create an account
jws = JsonWebSignature()
header = {
    "protected": {"alg": "ES256"},
    "header": {
        "jwk": public_key_bytes,
        "url": dir_urls['newAccount'],
        "nonce": nonce}
}
data = jws.serialize_json(header, b"", private_key)
account = requests.post(dir_urls['newAccount'],
                        json=data)
nonce = account.headers["Replay-Nonce"]
kid = re.search("^(.+/account/[^/]+)", account.json()['orders']).group(1)

# Start an order.
jws = JsonWebSignature()
header = {
    "protected": {"alg": "ES256"},
    "header": {
        "kid": kid,
        "url": dir_urls['newOrder'],
        "nonce": nonce}
}
payload = {
    "identifiers": [{"type": "dns", "value": zoobar_hostname}]
}
data = jws.serialize_json(header, payload, private_key)
order = requests.post(dir_urls['newOrder'],
                      json=data)
nonce = order.headers["Replay-Nonce"]

# Fetch challenges.
jws = JsonWebSignature()
header = {
    "protected": {"alg": "ES256"},
    "header": {
        "kid": kid,
        "url": order.json()['authorizations'][0],
        "nonce": nonce,}
}
data = jws.serialize_json(header, b"", private_key)
challenges = requests.post(order.json()["authorizations"][0],
                           json=data)
nonce = challenges.headers["Replay-Nonce"]

# Respond to the challenge.
token = challenges.json()["challenges"][0]["token"]
challenge_path = Path(f".well-known/acme-challenge/{token}")
challenge_path.parent.mkdir(exist_ok=True, parents=True)
challenge_path.write_text(f"{token}.{jwk.thumbprint()}")

jws = JsonWebSignature()
header = {
    "protected": {"alg": "ES256"},
    "header": {
        "kid": kid,
        "url": challenges.json()["challenges"][0]["url"],
        "nonce": nonce}
}
payload = {}
data = jws.serialize_json(header, payload, private_key)
validation = requests.post(challenges.json()["challenges"][0]["url"],
                            json=data)
nonce = validation.headers["Replay-Nonce"]

# Finalize the order.
jws = JsonWebSignature()
header = {
    "protected": {"alg": "ES256"},
    "header": {
        "kid": kid,
        "url": order.json()["finalize"],
        "nonce": nonce}
}
csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
    # Provide various details about who we are.
    x509.NameAttribute(NameOID.COMMON_NAME, zoobar_hostname),
    ])
    # Sign the CSR with our private key.
).sign(tls_key, hashes.SHA256())
encoded_csr = base64.urlsafe_b64encode(
    csr.public_bytes(serialization.Encoding.DER)
    )
payload = {
    "csr": encoded_csr.decode("utf-8")
}
data = jws.serialize_json(header, payload, private_key)
finalize = requests.post(order.json()["finalize"],
                         json=data)
nonce = finalize.headers["Replay-Nonce"]

# Get cert.
jws = JsonWebSignature()
header = {
    "protected": {"alg": "ES256"},
    "header": {
        "kid": kid,
        "url": finalize.json()["certificate"],
        "nonce": nonce}
}
data = jws.serialize_json(header, b"", private_key)
certificate = requests.post(finalize.json()["certificate"],
                     json=data)

with open(cert_pn, "wb") as f:
    f.write(certificate.content)
