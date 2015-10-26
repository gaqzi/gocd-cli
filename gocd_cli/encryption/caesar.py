"""
This is an example implementation of an encryption/decryption module
for settings. The API for a module like this is very simple, it has:

1. :func:`decrypt` function that only takes one argument, the
   string to decrypt
2. :func:`encrypt` function that only takes one argument, the
   string to encrypt

If you need to pass in an argument to encrypt/decrypt that is handled
out of band of gocd-cli, unless someone comes up with a great way and
convinces the maintainer that's the way to do it. :)
"""
import codecs


def decrypt(ciphertext):
    return codecs.decode(ciphertext, 'rot13')


def encrypt(plaintext):
    return codecs.encode(plaintext, 'rot13')
