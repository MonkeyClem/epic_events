from app.auth.auth import hash_password, verify_password, create_token, decode_token


def test_hash_and_verify_password():
    hashed = hash_password("abc123")
    assert verify_password("abc123", hashed)
    assert not verify_password("wrongpass", hashed)


def test_token_creation_and_decoding():
    token = create_token(42)
    assert decode_token(token) == 42
