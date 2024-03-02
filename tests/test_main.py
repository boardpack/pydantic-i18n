from decimal import Decimal
from typing import Dict, Tuple

import pytest

from pydantic import BaseModel, Field, ValidationError
from pydantic.color import Color
from pydantic_i18n import BaseLoader, DictLoader, PydanticI18n

translations = {
    "en_US": {
        "Field required": "field required",
        "value is not a valid color: {}": "value is not a valid color: {}",
        "Decimal input should have no more than {} digits in total": "Decimal input should have no more than {} digits in total",
    },
    "de_DE": {
        "Field required": "Feld erforderlich",
    },
    "es_AR": {
        "value is not a valid color: {}": "no es un color válido: {}",
    },
}


@pytest.fixture
def dict_loader() -> DictLoader:
    return DictLoader(translations)


@pytest.fixture
def tr() -> PydanticI18n:
    return PydanticI18n(translations)


def test_required_message():
    class User(BaseModel):
        name: str

    with pytest.raises(ValidationError) as e:
        User()

    assert e.value.errors()[0]["msg"] == "Field required"


def test_locales(tr: PydanticI18n):
    assert set(tr.locales) == set(translations)


@pytest.mark.parametrize(
    "translation_data",
    [
        translations,
        {
            "en_US": {
                "Field required": "Field required",
            },
            "de_DE": {
                "Field required": "Feld erforderlich",
            },
        },
    ],
    ids=[
        "multiple_keys",
        "single_keys",
    ],
)
def test_required_message_translation(translation_data: Dict[str, Dict[str, str]]):
    tr = PydanticI18n(translation_data)

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


@pytest.mark.parametrize(
    "loader",
    [
        # pytest.lazy_fixture("dict_loader"),
        pytest.lazy_fixture("babel_loader"),
    ],
)
def test_key_with_placeholder_at_the_end(loader: BaseLoader):
    class CoolSchema(BaseModel):
        color_field: Color

    tr = PydanticI18n(loader, default_locale="en_US")

    locale = "es_AR"
    with pytest.raises(ValidationError) as e:
        CoolSchema(color_field=(300, 300, 300, 1))

    translated_errors = tr.translate(e.value.errors(), locale=locale)
    assert (
        translated_errors[0]["msg"]
        == "no es un color válido: color values must be in the range 0 to 255"
    )


@pytest.mark.parametrize(
    "loader",
    [
        pytest.lazy_fixture("dict_loader"),
        pytest.lazy_fixture("babel_loader"),
    ],
)
def test_key_with_placeholder_in_the_middle(loader: BaseLoader):
    class T(BaseModel):
        decimal_field: Decimal = Field(max_digits=3)

    tr = PydanticI18n(loader, default_locale="en_US")

    locale = "en_US"
    with pytest.raises(ValidationError) as e:
        T(decimal_field=1111)

    translated_errors = tr.translate(e.value.errors(), locale=locale)
    assert (
        translated_errors[0]["msg"]
        == "Decimal input should have no more than 3 digits in total"
    )


def test_last_key_without_placeholder():
    _translations = {
        "en_US": {
            "field required": "field required",
            "value is not a valid integer": "Input should be a valid integer, unable to parse string as an integer",
        },
    }

    class User(BaseModel):
        user_id: int

    message = "value is not a valid integer"
    data = {"user_id": "abc"}

    tr = PydanticI18n(_translations)

    with pytest.raises(ValidationError) as e:
        User(**data)

    locale = "en_US"
    translated_errors = tr.translate(e.value.errors(), locale=locale)

    assert _translations[locale][message] == translated_errors[0]["msg"]


def test_multiple_placeholders():
    _translations = {
        "en_US": {
            "Tuple should have at most {} items after validation, not {}": "Tuple should have at most {} items after validation, not {}",
            "field required": "field required",
        },
        "de_DE": {
            "Tuple should have at most {} items after validation, not {}": "Tupel sollte nach der Validierung höchstens {} Elemente haben, nicht {}",
            "field required": "Feld erforderlich",
        },
    }

    class MyModel(BaseModel):
        value: Tuple[str, str]

    tr = PydanticI18n(_translations)

    with pytest.raises(ValidationError) as e:
        MyModel(value=("1", "2", "3"))

    locale = "de_DE"
    translated_errors = tr.translate(e.value.errors(), locale=locale)

    assert (
        translated_errors[0]["msg"]
        == "Tupel sollte nach der Validierung höchstens 2 Elemente haben, nicht 3"
    )


def test_invalid_regexp():
    _translations = {
        "en_US": {
            "This contains a partial [ regexp": "This contains a partial [ regexp",
        },
        "de_DE": {
            "This contains a partial [ regexp": "Hier ist eine partielle [ regexp",
        },
    }
    # all we test here is that loading doesn't crash
    PydanticI18n(_translations)


def test_valid_regexp():
    _translations = {
        "en_US": {
            "This contains [a] regexp": "This contains [a] regexp",
        },
        "de_DE": {
            "This contains [a] regexp": "Hier ist [eine] regexp",
        },
    }

    tr = PydanticI18n(_translations)

    locale = "de_DE"
    translated_errors = tr.translate(
        [{"msg": "This contains [a] regexp"}], locale=locale
    )
    assert translated_errors[0]["msg"] == "Hier ist [eine] regexp"
