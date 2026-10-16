#!/usr/bin/env python3
"""Build a configured 'Spot it & answer in HEX' riddle page.
Usage: python3 make_riddle.py --image pic.png --answer "INV-4471" [--accept "4471"] \
         --passphrase-file secret.txt --question "..." --out ../riddle.html
Generates a fresh ECDH P-256 owner keypair. The public key is embedded in clear;
the private key + correct answer(s) are embedded only encrypted
(PBKDF2-SHA256 600k + AES-256-GCM) with the owner's passphrase."""
import argparse, base64, json, os, re, html
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
b64u=lambda b: base64.urlsafe_b64encode(b).rstrip(b"=").decode()
b64=lambda b: base64.b64encode(b).decode()
ITER=600000
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--image",required=True); p.add_argument("--answer",required=True)
    p.add_argument("--accept",action="append",default=[]); p.add_argument("--passphrase-file",required=True)
    p.add_argument("--question",default="Find the hidden item and type what you see.")
    p.add_argument("--title",default="Spot it & answer in HEX")
    p.add_argument("--template",default=os.path.join(os.path.dirname(__file__),"riddle_template.html"))
    p.add_argument("--out",required=True); a=p.parse_args()
    pw=open(a.passphrase_file).read().strip()
    k=ec.generate_private_key(ec.SECP256R1()); n=k.private_numbers()
    pub=k.public_key().public_bytes(serialization.Encoding.X962,serialization.PublicFormat.UncompressedPoint)
    jwk={"kty":"EC","crv":"P-256","d":b64u(n.private_value.to_bytes(32,"big")),
         "x":b64u(n.public_numbers.x.to_bytes(32,"big")),"y":b64u(n.public_numbers.y.to_bytes(32,"big"))}
    bundle=json.dumps({"jwk":jwk,"answers":[a.answer]+a.accept}).encode()
    salt,iv=os.urandom(16),os.urandom(12)
    key=PBKDF2HMAC(hashes.SHA256(),32,salt,ITER).derive(pw.encode())
    ct=AESGCM(key).encrypt(iv,bundle,None)
    cfg={"pub":b64(pub),"owner":{"iter":ITER,"salt":b64(salt),"iv":b64(iv),"ct":b64(ct)},
         "image":os.path.basename(a.image),"question":a.question,"title":a.title}
    t=open(a.template).read().replace("/*__CONFIG__*/null",json.dumps(cfg))
    open(a.out,"w").write(t); print("wrote",a.out)
if __name__=="__main__": main()
