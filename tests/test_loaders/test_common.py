from typing import Callable

import pytest

from pydantic_i18n import BabelLoader, BaseLoader, JsonLoader


@pytest.mark.parametrize(
    "loader",
    [
        pytest.lazy_fixture("json_loader"),
        pytest.lazy_fixture("dict_loader"),
        pytest.lazy_fixture("babel_loader"),
    ],
)
def test_get_locales(loader: BaseLoader):
    locales = loader.locales
    assert len(locales) >= 2
    for locale in ("en_US", "de_DE"):
        assert locale in locales


@pytest.mark.parametrize(
    "loader",
    [
        pytest.lazy_fixture("json_loader"),
        pytest.lazy_fixture("dict_loader"),
        pytest.lazy_fixture("babel_loader"),
    ],
)
def test_translation(loader: BaseLoader):
    assert loader.gettext("field required", "en_US") == "field required"
    assert loader.gettext("field required", "de_DE") == "Feld erforderlich"


@pytest.mark.parametrize(
    "loader",
    [
        pytest.lazy_fixture("json_loader"),
        pytest.lazy_fixture("dict_loader"),
        pytest.lazy_fixture("babel_loader"),
    ],
)
def test_unsupported_locale(loader: BaseLoader):
    locale = "fr_FR"

    with pytest.raises(ValueError) as e:
        loader.gettext("field required", locale)

    assert str(e.value) == f"Locale '{locale}' wasn't found."


@pytest.mark.parametrize(
    "loader",
    [
        pytest.lazy_fixture("json_loader"),
        pytest.lazy_fixture("dict_loader"),
        pytest.lazy_fixture("babel_loader"),
    ],
)
def test_unknown_key(loader: BaseLoader):
    assert loader.gettext("unknown key", "en_US") == "unknown key"


@pytest.mark.parametrize(
    "loader_class",
    [
        JsonLoader,
        BabelLoader,
    ],
)
def test_unexisted_dir(loader_class: Callable[[str], None]):
    unexisted_directory = "/unexisted_dir"

    with pytest.raises(OSError):
        loader_class(unexisted_directory)
