# backend/app/utils/_password_utils.py

import os
import hashlib
import binascii


def hash_password(password):
    # Generate a random salt
    salt = os.urandom(16)

    # Use pbkdf2_hmac to hash the password
    hashed_password = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, 100000
    )

    # Combine the salt and the hashed password
    stored_password = binascii.hexlify(salt + hashed_password)

    return stored_password.decode("utf-8")


def check_password(stored_password, provided_password):
    # Decode the stored password and get the salt
    salt = binascii.unhexlify(stored_password)[:16]

    # Get the hashed password
    stored_password = binascii.unhexlify(stored_password)[16:]

    # Use pbkdf2_hmac to hash the provided password
    hashed_password = hashlib.pbkdf2_hmac(
        "sha256", provided_password.encode("utf-8"), salt, 100000
    )

    # Compare the hashed password with the stored password
    return hashed_password == stored_password
