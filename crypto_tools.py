import random
import math


# -------------------------------- Функції для генерації RSA ключів --------------------------------

def is_prime(n):
    """Перевірка, чи є число простим"""
    if n < 2:
        return False

    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True


def generate_prime(min_val=100, max_val=1000):
    """Генерація випадкового простого числа в заданому діапазоні"""
    while True:
        num = random.randint(min_val, max_val)
        if is_prime(num):
            return num


def generate_rsa_keys():
    """Створення пари публічний/приватний ключ методом RSA"""
    p = generate_prime()  # Випадкове просте число p
    q = generate_prime()  # Випадкове просте число q

    while p == q:  # Перевірка, щоб p і q були різними
        q = generate_prime()

    n = p * q  # Модуль
    phi = (p - 1) * (q - 1)  # Функція Ейлера

    # Вибір випадкового відкритого експоненту, взаємно простого з phi
    def generate_coprime_exponent(phi):
        while True:
            e = generate_prime(2, phi - 1)
            if math.gcd(e, phi) == 1:
                return e

    e = generate_coprime_exponent(phi)

    # Обчислення приватного ключа d
    def mod_inverse(a, m):
        m0, x0, x1 = m, 0, 1
        while a > 1:
            q = a // m
            a, m = m, a % m
            x0, x1 = x1 - q * x0, x0
        return x1 + m0 if x1 < 0 else x1

    d = mod_inverse(e, phi)

    # Повертаємо ключі як строки
    public_key = f"{e},{n}"
    private_key = f"{d},{n}"
    return private_key, public_key



# -------------------------------- Функції для створення підпису --------------------------------

def simplified_hash(message, n):
    """Хеш-функція квадратичної згортки"""
    h = 0  # Н0 = 0
    for char in message:
        m = ord(char) - ord('a') + 1  # Номер букви в алфавіті (a=1, b=2, ...)
        h = (h + m) ** 2 % n
    return h


def sign_message(private_key, message):
    """Підписання повідомлення"""
    d, n = map(int, private_key.split(','))
    h = simplified_hash(message, n)  # Хеш повідомлення
    signature = pow(h, d, n)  # Підписання хешу (h^d mod n)
    return str(signature)


def verify_signature(public_key, message, signature):
    """Перевірка підпису повідомлення"""
    e, n = map(int, public_key.split(','))
    h = simplified_hash(message, n)  # Хеш повідомлення
    s = int(signature)
    h_from_signature = pow(s, e, n)  # Перевірка підпису (s^e mod n)
    return h == h_from_signature



# -------------------------------- Функції для шифрування методом гамування --------------------------------

def encrypt_message_gamma(message, key):
    """Шифрування повідомлення методом гамування (XOR)"""
    if not message or not key:
        raise ValueError("Повідомлення та ключ не можуть бути пустими")

    # Розширюємо ключ до довжини повідомлення повторенням
    extended_key = key * (len(message) // len(key) + 1)
    extended_key = extended_key[:len(message)]

    # Шифруємо кожен символ повідомлення
    encrypted = []
    for m_char, k_char in zip(message, extended_key):
        # XOR між ASCII кодами символів
        encrypted_char = ord(m_char) ^ ord(k_char)
        # Конвертуємо в hex і додаємо leading zero якщо потрібно
        encrypted.append(f"{encrypted_char:02x}")

    return ','.join(encrypted)


def decrypt_message_gamma(ciphertext, key):
    """Розшифрування повідомлення методом гамування (XOR)"""
    if not ciphertext or not key:
        raise ValueError("Шифротекст та ключ не можуть бути пустими")

    # Розбиваємо шифротекст на hex значення
    try:
        encrypted_chars = [int(x, 16) for x in ciphertext.split(',')]
    except ValueError:
        raise ValueError("Неправильний формат шифротексту")

    # Розширюємо ключ до довжини шифротексту
    extended_key = key * (len(encrypted_chars) // len(key) + 1)
    extended_key = extended_key[:len(encrypted_chars)]

    # Розшифровуємо кожен символ
    decrypted = []
    for enc_char, k_char in zip(encrypted_chars, extended_key):
        # XOR між зашифрованим значенням і ASCII кодом символу ключа
        decrypted_char = enc_char ^ ord(k_char)
        decrypted.append(chr(decrypted_char))
    return ''.join(decrypted)
