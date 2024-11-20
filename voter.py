from crypto_tools import *
import numpy as np

class Voter:
    def __init__(self, name):
        self.private_sign, self.public_sign = generate_rsa_keys()
        self.voter_name = name

    def sign_message(self, message):
        """Підписання повідомлення"""
        d, n = map(int, self.private_sign.split(','))
        h = simplified_hash(message, n)  # Хеш повідомлення
        signature = pow(h, d, n)  # Підписання хешу (h^d mod n)

        return str(signature)