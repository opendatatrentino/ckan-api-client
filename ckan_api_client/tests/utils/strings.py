"""
String generation functions.
"""

import binascii
import os
import random
import string


def generate_password(length=20):
    return binascii.hexlify(os.urandom(length))


def generate_random_alphanum(length=10):
    charset = string.ascii_letters + string.digits
    return ''.join(random.choice(charset) for _ in xrange(length))
