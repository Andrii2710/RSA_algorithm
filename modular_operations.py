import hashlib
import random

def euclidean_algorithm(a, b):
    while b:
        a, b = b, a % b
    return a

def extended_euclidean_algorithm(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_euclidean_algorithm(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def mod_inverse(e, phi):
    gcd, x, y = extended_euclidean_algorithm(e, phi)
    if gcd != 1:
        raise ValueError("Modular inverse does not exist")
    return x % phi

def is_prime(num):
    if num < 2:
        return False
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            return False
    return True

def get_hash(message):
    return hashlib.sha256(message.encode()).hexdigest()

def encrypt(public_key, message):
    e, n = public_key
    encrypted_msg = [pow(ord(char), e, n) for char in message]
    return encrypted_msg

def decrypt(private_key, cipher):
    d, n = private_key
    decrypted_chars = [chr(pow(char, d, n)) for char in cipher]
    return "".join(decrypted_chars)
