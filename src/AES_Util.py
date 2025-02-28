from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import base64


def aes_decrypt_by_bytes(encrypt_bytes: bytes, decrypt_key: str) -> str:
    key = decrypt_key.encode('utf-8')[:16]

    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
    decryptor = cipher.decryptor()

    decrypted_padded_bytes = decryptor.update(encrypt_bytes) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    decrypted_bytes = unpadder.update(decrypted_padded_bytes) + unpadder.finalize()

    return decrypted_bytes.decode('utf-8')


def aes_encrypt_by_bytes(plain_text: str, encrypt_key: str) -> bytes:
    key = encrypt_key.encode('utf-8')[:16]

    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plain_text.encode('utf-8')) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
    encryptor = cipher.encryptor()

    encrypted_bytes = encryptor.update(padded_data) + encryptor.finalize()
    return base64.b64encode(encrypted_bytes)
