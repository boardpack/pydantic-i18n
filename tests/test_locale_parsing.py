from typing import Any, Dict

import pytest

from pydantic_i18n import PydanticI18n


@pytest.mark.parametrize(
    "kwargs, expected_language",
    [
        [{"default": "value"}, "value"],
        [{"url": "https://en.example.com"}, "en_US"],
        [{"url": "https://example.example.com"}, None],
        [{"url": "https://example.com/en"}, "en_US"],
        [{"url": "https://example.com/en/"}, "en_US"],
        [{"url": "https://example.com/en-us"}, "en_US"],
        [{"url": "https://example.com/en-us/"}, "en_US"],
        [{"url": "https://example.com/en-US"}, "en_US"],
        [{"url": "https://example.com/en-US/"}, "en_US"],
        [{"url": "https://example.com/example"}, None],
        [{"url": "https://example.com/", "default": "en"}, "en"],
        [{"headers": {"Accept-Language": "de"}}, "de_DE"],
        [{"headers": {"Accept-Language": "de-at"}}, "de_AT"],
        [{"headers": {"Accept-Language": "es-es"}}, "es_ES"],
        [{"headers": {"Accept-Language": ""}}, None],
        [{"headers": {"Accept-Language": ""}, "default": "en"}, "en"],
        [{"headers": {"Accept-Language": "es1"}, "default": "en"}, "en"],
        [{"headers": {"accept-language": "de"}}, "de_DE"],
        [{"headers": {"accept-language": "de-at"}}, "de_AT"],
        [{"headers": {"accept-language": "es-es"}}, "es_ES"],
        [{"headers": {"accept-language": ""}}, None],
        [{"headers": {"accept-language": ""}, "default": "en"}, "en"],
    ],
)
def test_language_parsing(
    kwargs: Dict[str, Any],
    expected_language: str,
):
    assert PydanticI18n.get_locale_from_request(**kwargs) == expected_language
