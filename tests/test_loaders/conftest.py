import json

import pytest

from pydantic_i18n import DictLoader, JsonLoader


@pytest.fixture
def json_translations_directory(tmp_path) -> str:
    package_name = "translations"
    default_translation_filename = "en_US.json"
    de_translation_filename = "de_DE.json"

    package = tmp_path / package_name
    package.mkdir()

    fp = package / default_translation_filename
    fp.touch()
    fp.write_text(
        json.dumps(
            {
                "field required": "field required",
            }
        )
    )

    fp = package / de_translation_filename
    fp.touch()
    fp.write_text(
        json.dumps(
            {
                "field required": "Feld erforderlich",
            }
        )
    )

    yield str(package)


@pytest.fixture
def json_loader(json_translations_directory: str) -> JsonLoader:
    return JsonLoader(json_translations_directory)


@pytest.fixture
def dict_loader() -> DictLoader:
    translations = {
        "en_US": {
            "field required": "field required",
        },
        "de_DE": {
            "field required": "Feld erforderlich",
        },
    }

    return DictLoader(translations)
