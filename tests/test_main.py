import json
import re
from typing import Dict

import pytest

from pydantic import BaseModel, ValidationError
from pydantic_i18n import BaseLoader, DictLoader, PydanticI18n

translations = {
    "en_US": {
        "field required": "field required",
    },
    "de_DE": {
        "field required": "Feld erforderlich",
    },
}


@pytest.fixture
def tr() -> PydanticI18n:
    loader = DictLoader(translations)
    return PydanticI18n(loader)


def test_required_message():
    class User(BaseModel):
        name: str

    with pytest.raises(ValidationError) as e:
        User()

    assert e.value.errors()[0]["msg"] == "field required"


def test_locales(tr: PydanticI18n):
    assert set(tr.locales) == set(translations)


def test_required_message_translation(tr: PydanticI18n):
    class User(BaseModel):
        name: str

    with pytest.raises(ValidationError) as e:
        User()

    translated_errors = tr.translate(e.value.errors(), locale="de_DE")
    assert (
        translated_errors[0]["msg"] == translations["de_DE"][e.value.errors()[0]["msg"]]
    )


def test_multiple_fields_errors(tr: PydanticI18n):
    class User(BaseModel):
        first_name: str
        last_name: str

    with pytest.raises(ValidationError) as e:
        User()

    errors = e.value.errors()
    translated_errors = tr.translate(errors, locale="de_DE")

    for original, translated in zip(errors, translated_errors):
        assert translated["msg"] == translations["de_DE"][original["msg"]]


def test_unsupported_locale(tr: PydanticI18n):
    class User(BaseModel):
        name: str

    with pytest.raises(ValidationError) as validation_error:
        User()

    locale = "fr_FR"
    with pytest.raises(ValueError) as e:
        tr.translate(validation_error.value.errors(), locale=locale)

    assert str(e.value) == f"Locale '{locale}' wasn't found."


def test_dict_source():
    tr = PydanticI18n(translations)
    assert isinstance(tr.source, BaseLoader)


def _test_pydantic_messages(data: Dict[str, str]) -> None:
    assert len(data)
    for k, v in data.items():
        assert isinstance(k, str)
        assert k == v


def test_pydantic_messages_json():
    output = PydanticI18n.get_pydantic_messages(output="json")
    assert isinstance(output, str)

    dict_output = json.loads(output)
    _test_pydantic_messages(dict_output)


def test_pydantic_messages_dict():
    output = PydanticI18n.get_pydantic_messages(output="dict")
    assert isinstance(output, dict)
    _test_pydantic_messages(output)


def test_pydantic_messages_dict_by_default():
    output = PydanticI18n.get_pydantic_messages()
    assert isinstance(output, dict)
    _test_pydantic_messages(output)


def test_pydantic_messages_babel():
    output = PydanticI18n.get_pydantic_messages(output="babel")
    assert isinstance(output, str)

    dict_output = dict(
        zip(
            re.findall('msgid "(.+)"\n', output),
            re.findall('msgstr "(.+)"\n', output),
        )
    )
    _test_pydantic_messages(dict_output)
