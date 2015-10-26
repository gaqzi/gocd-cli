from gocd_cli.encryption import caesar


def test_encrypt():
    assert caesar.encrypt('hello') == 'uryyb'


def test_decrypt():
    assert caesar.decrypt('uryyb') == 'hello'
