"""Typed settings loaded when an application is created."""

import os
from pathlib import Path
from typing import Annotated, Any, Literal, Self

import yaml
from dotenv import dotenv_values
from pydantic import BaseModel, ConfigDict, Field, SecretStr, model_validator

Text = Annotated[str, Field(min_length=1, max_length=2000)]
Slug = Annotated[str, Field(pattern=r"^[a-z][a-z0-9-]{0,63}$")]


class ConfigDefaults(BaseModel):
    model_config = ConfigDict(extra="ignore")

    debug: bool
    web_settings_file: Path | None
    database_url: SecretStr
    cookie_secure: bool
    session_lifetime_seconds: int = Field(ge=60, le=604800)


def _settings_path(path: str | Path | None = None) -> Path:
    selected = path or os.environ.get("APP_SETTINGS")
    if selected is None:
        raise ValueError(
            "Set APP_SETTINGS or pass --settings with a settings YAML file."
        )
    return Path(selected)


def load_config_defaults(path: str | Path | None = None) -> ConfigDefaults:
    config_path = _settings_path(path)
    try:
        content: Any = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"Cannot load application config from {config_path}") from exc
    defaults = ConfigDefaults.model_validate(content)
    if (
        defaults.web_settings_file is not None
        and not defaults.web_settings_file.is_absolute()
    ):
        defaults.web_settings_file = config_path.parent / defaults.web_settings_file
    return defaults


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: Text
    title: Text
    summary: Text
    status: Text
    owner: Text
    detail: Text


class Page(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: Slug
    label: Text
    title: Text
    description: Text
    kind: Literal["overview", "collection"] = "collection"
    empty_message: Text = "There are no items on this page yet."
    records: list[Record] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_records(self) -> Self:
        if len({record.key for record in self.records}) != len(self.records):
            raise ValueError("Record keys must be unique within each page")
        if self.kind == "overview" and self.records:
            raise ValueError("Overview pages summarize collections; put records there")
        return self


class WebConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: Literal[1]
    name: Text
    workspace: Text
    notice: Text
    home: Slug
    pages: list[Page] = Field(min_length=1, max_length=30)

    @model_validator(mode="after")
    def validate_pages(self) -> Self:
        slugs = [page.slug for page in self.pages]
        if len(set(slugs)) != len(slugs):
            raise ValueError("Page slugs must be unique")
        if self.home not in slugs:
            raise ValueError("Home must reference a configured page slug")
        reserved = {
            "health",
            "docs",
            "redoc",
            "static",
            "login",
            "logout",
            "openapi.json",
        }
        if reserved.intersection(slugs):
            raise ValueError("Page slugs cannot use reserved application routes")
        return self


def load_web_config(path: Path | None = None) -> WebConfig:
    if path is None:
        path = load_config_defaults().web_settings_file
    if path is None:
        raise ValueError("Set web_settings_file in the settings YAML file.")
    try:
        content = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"Cannot load web settings from {path}") from exc
    return WebConfig.model_validate(content)


class Settings(BaseModel):
    model_config = ConfigDict(extra="ignore")

    debug: bool
    web_settings_file: Path | None

    database_url: SecretStr
    cookie_secure: bool
    session_lifetime_seconds: int = Field(ge=60, le=604800)

    def __init__(
        self, *, settings_file: str | Path | None = None, **values: Any
    ) -> None:
        env_file = values.pop("_env_file", None)
        data = load_config_defaults(settings_file).model_dump()
        data.update(_load_env_file_values(env_file))
        data.update(values)
        super().__init__(**data)


def _load_env_file_values(env_file: Any) -> dict[str, str]:
    if env_file is None:
        return {}
    if isinstance(env_file, (str, Path)):
        env_files = [env_file]
    else:
        env_files = list(env_file)
    values: dict[str, str] = {}
    for path in env_files:
        values.update(_settings_values_from_mapping(dotenv_values(path)))
    return values


def _settings_values_from_mapping(mapping: Any) -> dict[str, str]:
    field_names = set(Settings.model_fields)
    values: dict[str, str] = {}
    for key, value in mapping.items():
        if value is None:
            continue
        field_name = key.lower()
        if field_name in field_names:
            values[field_name] = str(value)
    return values
