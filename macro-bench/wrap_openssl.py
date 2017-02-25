import os
from cryptoutil import CryptoUtil
from cryptoutil import RSA_KEY_PEM
#from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends.openssl import backend as openssl

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.hashes import SHA512, SHA1
from cryptography.hazmat.primitives.asymmetric.padding import PSS, OAEP, MGF1
from cryptography.exceptions import InvalidSignature, UnsupportedAlgorithm
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding

from cryptography.hazmat.primitives.asymmetric import ec


class OpenSSLWrapper:
    backend = openssl
    def __init__(self):
        pass

    def encrypt(self, s, key, iv, mode):
        cipher = Cipher(algorithms.AES(key), mode,
            backend=OpenSSLWrapper.backend)
        encryptor = cipher.encryptor()
        ct = encryptor.update(s) + encryptor.finalize()
        return iv + ct

    def decrypt(self, s, key, mode):
        iv = s[:16]
        cipher = Cipher(algorithms.AES(key), mode,
            backend=OpenSSLWrapper.backend)
        decryptor = cipher.decryptor()
        p = decryptor.update(s[16:]) + decryptor.finalize()
        return p

class CBC_CIPHER(OpenSSLWrapper):
    def __init__(self):
        pass

    def encrypt(self, s, key, iv):
        s = CryptoUtil.pad(s)
        return super(CBC_CIPHER, self).encrypt(s, key, iv, modes.CBC(iv))

    def decrypt(self, s, key):
        iv = s[:16]
        d = super(CBC_CIPHER, self).decrypt(s, key, modes.CBC(iv))
        return CryptoUtil.unpad(d)

class CTR_CIPHER(OpenSSLWrapper):
    def __init__(self):
        pass

    def encrypt(self, s, key, iv):
        return super(CTR_CIPHER, self).encrypt(s, key, iv, modes.CTR(iv))

    def decrypt(self, s, key):
        iv = s[:16]
        return super(CTR_CIPHER, self).decrypt(s, key, modes.CTR(iv))

class GCM_CIPHER(OpenSSLWrapper):
    def __init__(self):
        pass

    def encrypt(self, s, key, iv):
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv),
            backend=OpenSSLWrapper.backend)
        encryptor = cipher.encryptor()
        ct = encryptor.update(s) + encryptor.finalize()
        return iv + ct + encryptor.tag

    def decrypt(self, s, key):
        iv = s[:16]
        tag = s[-16:]
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag),
            backend=OpenSSLWrapper.backend)
        decryptor = cipher.decryptor()
        return decryptor.update(s[16:-16]) + decryptor.finalize()


class RSA_SIGNER(OpenSSLWrapper):
    def __init__(self):
        #self.signature_size = 512
        self.u_pri_key = rsa.generate_private_key(public_exponent=65537,
            key_size=CryptoUtil.get_strength_level('rsa'),
            backend=OpenSSLWrapper.backend)
        self.u_pub_key = self.u_pri_key.public_key()

    def sign(self, msg):
        signer = self.u_pri_key.signer(PSS(mgf=MGF1(SHA512()),
            salt_length=PSS.MAX_LENGTH), SHA512())
        signer.update(msg)
        signature = signer.finalize()
        sig_length = (len(signature)).to_bytes(4, byteorder='big')
        return sig_length + signature + msg

    def verify(self, msg):
        sig_length_bytes = msg[:4]
        sig_length = int.from_bytes(sig_length_bytes, byteorder='big')
        signature = msg[4:4+sig_length]
        s = msg[4+sig_length:]
        #recv_sig = msg[:self.signature_size] # rsa sign are 512 bytes
        #s = msg[self.signature_size:]
        verifier = self.u_pub_key.verifier(
            signature,
            PSS(mgf=MGF1(SHA512()), salt_length=PSS.MAX_LENGTH), SHA512())
        verifier.update(s)
        verifier.verify()
        return s

class ECDSA_SIGNER(OpenSSLWrapper):
    def __init__(self):
        self.private_key = ec.generate_private_key(
            CryptoUtil.get_strength_level('ecc'), 
            backend=OpenSSLWrapper.backend)
        self.public_key = self.private_key.public_key()

    def sign(self, msg):
        signer = self.private_key.signer(ec.ECDSA(hashes.SHA512()))
        signer.update(msg)
        signature = signer.finalize()
        sig_length = (len(signature)).to_bytes(4, byteorder='big')
        return sig_length + signature + msg

    def verify(self, msg):
        sig_length_bytes = msg[:4]
        sig_length = int.from_bytes(sig_length_bytes, byteorder='big')
        signature = msg[4:4+sig_length]
        s = msg[4+sig_length:]
        verifier = self.public_key.verifier(signature, ec.ECDSA(hashes.SHA512()))
        verifier.update(s)
        verifier.verify()
        return s
