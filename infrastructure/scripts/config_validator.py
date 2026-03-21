from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
AWS_REGION_PATTERN = re.compile(r"^[a-z]{2}-[a-z]+-\d$")
INSTANCE_TYPE_PATTERN = re.compile(r"^[a-z]\d[a-z]?\.[a-z0-9]+$")


@dataclass(slots=True)
class ValidationResult:
    is_valid: bool
    errors: list[str] = field(default_factory=list)


class ConfigValidator:
    def __init__(self) -> None:
        self._aws_profiles = self._load_aws_profiles()

    @staticmethod
    def _load_yaml(path: str | Path) -> dict[str, Any]:
        config_path = Path(path)
        if not config_path.exists():
            msg = f"Configuration file not found: {config_path}"
            raise FileNotFoundError(msg)
        content = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        if not isinstance(content, dict):
            return {}
        return content

    @staticmethod
    def _load_aws_profiles() -> set[str]:
        profiles: set[str] = set()
        for aws_file in (Path.home() / ".aws" / "credentials", Path.home() / ".aws" / "config"):
            if not aws_file.exists():
                continue
            for line in aws_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("[") and line.endswith("]"):
                    profile_name = line.strip("[]").removeprefix("profile ")
                    if profile_name:
                        profiles.add(profile_name)
        return profiles

    def validate_aws_config(self, config_path: str | Path) -> ValidationResult:
        errors: list[str] = []
        data = self._load_yaml(config_path)

        aws = data.get("aws", {}) if isinstance(data.get("aws", {}), dict) else {}
        project = data.get("project", {}) if isinstance(data.get("project", {}), dict) else {}
        instance = data.get("instance", {}) if isinstance(data.get("instance", {}), dict) else {}
        security = data.get("security", {}) if isinstance(data.get("security", {}), dict) else {}
        monitoring = data.get("monitoring", {}) if isinstance(data.get("monitoring", {}), dict) else {}

        profile = str(aws.get("profile", "")).strip()
        region = str(aws.get("region", "")).strip()
        owner = str(project.get("owner", "")).strip()
        instance_type = str(instance.get("type", "")).strip()
        volume_size = instance.get("volume_size")

        if not profile:
            errors.append("Missing required value: aws.profile")
        elif self._aws_profiles and profile not in self._aws_profiles:
            available = ", ".join(sorted(self._aws_profiles))
            errors.append(f"AWS profile '{profile}' does not exist. Available: {available}")

        if not region:
            errors.append("Missing required value: aws.region")
        elif not AWS_REGION_PATTERN.match(region):
            errors.append(f"Invalid AWS region format: {region}")

        if owner and not EMAIL_PATTERN.match(owner):
            errors.append(f"Invalid project.owner email format: {owner}")

        alert_email = str(monitoring.get("alert_email", "")).strip()
        if alert_email and not EMAIL_PATTERN.match(alert_email):
            errors.append(f"Invalid monitoring.alert_email format: {alert_email}")

        if not instance_type:
            errors.append("Missing required value: instance.type")
        elif not INSTANCE_TYPE_PATTERN.match(instance_type):
            errors.append(f"Invalid instance type format: {instance_type}")

        if volume_size is None:
            errors.append("Missing required value: instance.volume_size")
        elif not isinstance(volume_size, int) or volume_size < 20:
            errors.append("instance.volume_size must be an integer >= 20")

        self._validate_cidrs(errors, security.get("ssh_allowed_cidrs"), "security.ssh_allowed_cidrs")
        self._validate_cidrs(errors, security.get("langfuse_allowed_cidrs"), "security.langfuse_allowed_cidrs")

        return ValidationResult(is_valid=not errors, errors=errors)

    def validate_langfuse_config(self, config_path: str | Path) -> ValidationResult:
        errors: list[str] = []
        data = self._load_yaml(config_path)

        langfuse = data.get("langfuse", {}) if isinstance(data.get("langfuse", {}), dict) else {}
        version = str(langfuse.get("version", "")).strip()
        if not version:
            errors.append("Missing required value: langfuse.version")
        elif not re.fullmatch(r"\d+(\.\d+)?", version):
            errors.append(f"langfuse.version must be numeric (e.g. '3' or '3.0'), got: {version}")

        init = langfuse.get("init", {}) if isinstance(langfuse.get("init", {}), dict) else {}
        admin_email = str(init.get("admin_email", "")).strip()
        if admin_email and not EMAIL_PATTERN.match(admin_email):
            errors.append(f"Invalid langfuse.init.admin_email format: {admin_email}")

        resources = langfuse.get("resources", {}) if isinstance(langfuse.get("resources", {}), dict) else {}
        for service_name, resource in resources.items():
            if not isinstance(resource, dict):
                errors.append(f"langfuse.resources.{service_name} must be a mapping")
                continue
            memory_value = str(resource.get("memory", "")).strip()
            if memory_value:
                self._validate_memory_limit(
                    errors,
                    memory_value,
                    f"langfuse.resources.{service_name}.memory",
                )

        security = langfuse.get("security", {}) if isinstance(langfuse.get("security", {}), dict) else {}
        timeout = security.get("session_timeout_minutes")
        if timeout is None:
            errors.append("Missing required value: langfuse.security.session_timeout_minutes")
        elif not isinstance(timeout, int) or timeout <= 0 or timeout > 1440:
            errors.append("langfuse.security.session_timeout_minutes must be an integer between 1 and 1440")

        return ValidationResult(is_valid=not errors, errors=errors)

    @staticmethod
    def _validate_cidrs(errors: list[str], cidrs: Any, field_name: str) -> None:
        if not isinstance(cidrs, list) or not cidrs:
            errors.append(f"{field_name} must be a non-empty list")
            return
        for cidr in cidrs:
            if not isinstance(cidr, str):
                errors.append(f"{field_name} contains a non-string value")
                continue
            try:
                ipaddress.ip_network(cidr, strict=False)
            except ValueError:
                errors.append(f"Invalid CIDR in {field_name}: {cidr}")

    @staticmethod
    def _validate_memory_limit(errors: list[str], value: str, field_name: str) -> None:
        mi_match = re.fullmatch(r"(\d+)Mi", value)
        gi_match = re.fullmatch(r"(\d+)Gi", value)
        if mi_match:
            if int(mi_match.group(1)) < 512:
                errors.append(f"{field_name} must be >= 512Mi")
            return
        if gi_match:
            if int(gi_match.group(1)) < 1:
                errors.append(f"{field_name} must be >= 1Gi")
            return
        errors.append(f"{field_name} must be in Mi or Gi format (e.g. 512Mi, 2Gi)")


def _format_errors(errors: list[str]) -> str:
    return "\n".join(f"- {error}" for error in errors)


def main() -> int:
    validator = ConfigValidator()

    aws_result = validator.validate_aws_config("infrastructure/config/aws-config.yaml")
    if not aws_result.is_valid:
        print("AWS configuration validation failed:")
        print(_format_errors(aws_result.errors))
        return 1

    langfuse_result = validator.validate_langfuse_config("infrastructure/config/langfuse-config.yaml")
    if not langfuse_result.is_valid:
        print("Langfuse configuration validation failed:")
        print(_format_errors(langfuse_result.errors))
        return 1

    print("Configuration validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())