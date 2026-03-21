from __future__ import annotations

import base64
import secrets
import string


ALPHANUM = string.ascii_letters + string.digits


def generate_nextauth_secret() -> str:
    return base64.b64encode(secrets.token_bytes(32)).decode("utf-8")


def generate_salt() -> str:
    return base64.b64encode(secrets.token_bytes(32)).decode("utf-8")


def generate_encryption_key() -> str:
    return secrets.token_hex(32)


def generate_password(length: int = 32) -> str:
    if length < 32:
        msg = "Password length must be at least 32"
        raise ValueError(msg)
    return "".join(secrets.choice(ALPHANUM) for _ in range(length))


def build_secret_map() -> dict[str, str]:
    return {
        "nextauth-secret": generate_nextauth_secret(),
        "salt": generate_salt(),
        "encryption-key": generate_encryption_key(),
        "postgres-password": generate_password(),
        "clickhouse-password": generate_password(),
        "minio-password": generate_password(),
        "admin-password": generate_password(),
        "api-secret-key": generate_nextauth_secret(),
    }