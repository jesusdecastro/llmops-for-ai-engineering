#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, cast

import boto3
import yaml


SECRET_KEYS = {
    "nextauth-secret": "NEXTAUTH_SECRET",
    "salt": "SALT",
    "encryption-key": "ENCRYPTION_KEY",
    "postgres-password": "POSTGRES_PASSWORD",
    "clickhouse-password": "CLICKHOUSE_PASSWORD",
    "minio-password": "MINIO_ROOT_PASSWORD",
    "admin-password": "LANGFUSE_INIT_USER_PASSWORD",
    "api-secret-key": "LANGFUSE_INIT_PROJECT_SECRET_KEY",
}


def _load_yaml(path: Path) -> dict[str, Any]:
    content = yaml.safe_load(path.read_text(encoding="utf-8"))
    if isinstance(content, dict):
        return cast(dict[str, Any], content)
    return {}


def _fetch_ssm_secrets(prefix: str, region: str, profile: str | None) -> dict[str, str]:
    session_kwargs: dict[str, str] = {"region_name": region}
    if profile:
        session_kwargs["profile_name"] = profile

    session = boto3.Session(**session_kwargs)
    ssm = session.client("ssm")

    names = [f"{prefix}/{name}" for name in SECRET_KEYS]
    response = cast(dict[str, Any], ssm.get_parameters(Names=names, WithDecryption=True))

    invalid = response.get("InvalidParameters", [])
    if invalid:
        invalid_text = ", ".join(sorted(invalid))
        msg = f"No se encontraron parámetros SSM requeridos: {invalid_text}"
        raise RuntimeError(msg)

    parameters = cast(list[dict[str, str]], response.get("Parameters", []))
    values_by_name = {param["Name"]: param["Value"] for param in parameters}
    env_values: dict[str, str] = {}

    for short_name, env_name in SECRET_KEYS.items():
        full_name = f"{prefix}/{short_name}"
        value = values_by_name.get(full_name)
        if not value:
            msg = f"Falta valor para parámetro SSM: {full_name}"
            raise RuntimeError(msg)
        env_values[env_name] = value

    return env_values


def _dict_value(data: dict[str, Any], key: str) -> dict[str, Any]:
    raw = data.get(key)
    if isinstance(raw, dict):
        return cast(dict[str, Any], raw)
    return {}


def _str_value(data: dict[str, Any], key: str, default: str) -> str:
    return str(data.get(key, default))


def _int_value(data: dict[str, Any], key: str, default: int) -> int:
    return int(data.get(key, default))


def _base_env(
    langfuse: dict[str, Any],
    init: dict[str, Any],
    postgres: dict[str, Any],
    clickhouse: dict[str, Any],
    redis: dict[str, Any],
    minio: dict[str, Any],
    public_host: str,
    data_dir: str,
) -> dict[str, str]:
    port = _int_value(langfuse, "port", 3000)
    return {
        "LANGFUSE_VERSION": _str_value(langfuse, "version", "3"),
        "LANGFUSE_PORT": str(port),
        "DATA_DIR": data_dir,
        "NEXTAUTH_URL": f"http://{public_host}:{port}",
        "POSTGRES_DB": _str_value(postgres, "database", "langfuse"),
        "POSTGRES_USER": _str_value(postgres, "user", "langfuse"),
        "POSTGRES_PORT": str(_int_value(postgres, "port", 5432)),
        "CLICKHOUSE_DB": _str_value(clickhouse, "database", "langfuse"),
        "CLICKHOUSE_USER": _str_value(clickhouse, "user", "langfuse"),
        "CLICKHOUSE_HTTP_PORT": str(_int_value(clickhouse, "http_port", 8123)),
        "CLICKHOUSE_NATIVE_PORT": str(_int_value(clickhouse, "native_port", 9000)),
        "REDIS_PORT": str(_int_value(redis, "port", 6379)),
        "MINIO_ROOT_USER": _str_value(minio, "root_user", "langfuse"),
        "MINIO_BUCKET": _str_value(minio, "bucket", "langfuse"),
        "MINIO_PORT": str(_int_value(minio, "port", 9000)),
        "MINIO_CONSOLE_PORT": str(_int_value(minio, "console_port", 9001)),
        "LANGFUSE_INIT_USER_EMAIL": _str_value(init, "admin_email", "admin@langfuse.local"),
        "LANGFUSE_INIT_USER_NAME": _str_value(init, "admin_name", "Admin"),
        "LANGFUSE_INIT_ORG_ID": _str_value(init, "org_id", "org-workshop"),
        "LANGFUSE_INIT_ORG_NAME": _str_value(init, "org_name", "Workshop"),
        "LANGFUSE_INIT_PROJECT_ID": _str_value(init, "project_id", "proj-workshop"),
        "LANGFUSE_INIT_PROJECT_NAME": _str_value(init, "project_name", "techshop-agent"),
        "LANGFUSE_INIT_PROJECT_PUBLIC_KEY": _str_value(
            init,
            "project_public_key",
            "pk-lf-workshop",
        ),
        "LANGFUSE_SESSION_MAX_AGE": "28800",
        "LANGFUSE_ALLOW_SIGNUP": "false",
    }


def _build_env(
    config: dict[str, Any],
    secrets: dict[str, str],
    public_host: str,
    data_dir: str,
) -> dict[str, str]:
    langfuse = _dict_value(config, "langfuse")
    init = _dict_value(langfuse, "init")

    postgres = _dict_value(langfuse, "postgres")
    clickhouse = _dict_value(langfuse, "clickhouse")
    redis = _dict_value(langfuse, "redis")
    minio = _dict_value(langfuse, "minio")

    env = _base_env(
        langfuse,
        init,
        postgres,
        clickhouse,
        redis,
        minio,
        public_host,
        data_dir,
    )

    env.update(secrets)

    env["DATABASE_URL"] = (
        f"postgresql://{env['POSTGRES_USER']}:{env['POSTGRES_PASSWORD']}@postgres:5432/{env['POSTGRES_DB']}"
    )
    env["DIRECT_URL"] = env["DATABASE_URL"]
    env["CLICKHOUSE_URL"] = (
        f"http://{env['CLICKHOUSE_USER']}:{env['CLICKHOUSE_PASSWORD']}@clickhouse:8123/{env['CLICKHOUSE_DB']}"
    )
    env["CLICKHOUSE_MIGRATION_URL"] = env["CLICKHOUSE_URL"]
    env["REDIS_CONNECTION_STRING"] = "redis://redis:6379"

    return env


def _write_env_file(path: Path, values: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"{key}={value}" for key, value in values.items()]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Genera .env para Langfuse desde YAML + SSM")
    parser.add_argument(
        "--config",
        default="infrastructure/config/langfuse-config.yaml",
        help="Ruta a langfuse-config.yaml",
    )
    parser.add_argument(
        "--output",
        default="infrastructure/generated/langfuse.env",
        help="Ruta de salida del archivo .env",
    )
    parser.add_argument("--aws-region", required=True, help="Región AWS")
    parser.add_argument("--parameter-prefix", required=True, help="Prefijo de parámetros SSM")
    parser.add_argument("--public-host", required=True, help="Host/IP público para NEXTAUTH_URL")
    parser.add_argument("--aws-profile", default=None, help="AWS profile opcional")
    parser.add_argument("--data-dir", default="/opt/langfuse/data", help="Ruta DATA_DIR")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    config = _load_yaml(Path(args.config))
    secrets = _fetch_ssm_secrets(args.parameter_prefix, args.aws_region, args.aws_profile)
    env = _build_env(config, secrets, args.public_host, args.data_dir)
    _write_env_file(Path(args.output), env)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
