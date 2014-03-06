"""
String generation functions.
"""

import binascii
import hashlib
import os
import random
import string


def generate_password(length=20):
    """
    Generate random password of the given ``length``.

    Beware that the string will be generate as random data from urandom,
    and returned as headecimal string of twice the ``length``.
    """
    return binascii.hexlify(os.urandom(length))


def generate_random_alphanum(length=10):
    """Generate a random string, made of ascii letters + digits"""
    charset = string.ascii_letters + string.digits
    return ''.join(random.choice(charset) for _ in xrange(length))


def gen_random_id(length=10):
    """Generate a random id, made of lowercase ascii letters + digits"""
    charset = string.ascii_lowercase + string.digits
    return ''.join(random.choice(charset) for _ in xrange(length))


def gen_dataset_name():
    """Generate a random dataset name"""
    return "dataset-{0}".format(gen_random_id())


def gen_picture(s, size=200):
    """Generate URL to picture from some text hash"""
    return gen_robohash(s, size)


def gen_gravatar(s, size=200):
    """Return URL for gravatar of md5 of string ``s``"""
    h = hashlib.md5(s).hexdigest()
    return ('http://www.gravatar.com/avatar/{0}.jpg'
            '?d=identicon&f=y&s={1}'.format(h, size))


def gen_robohash(s, size=200):
    """Return URL for robohash pic for sha1 hash of string ``s``"""
    h = hashlib.sha1(s).hexdigest()
    return ('http://robohash.org/{0}.png?size={1}x{1}&bgset=bg2&set=set1'
            .format(h, size))
