from typing import Callable

import pytest
from _pytest.fixtures import FixtureRequest

from pydantic_i18n import BabelLoader, JsonLoader


@pytest.mark.parametrize(
    "loader_fixture_name",
    [
        "json_loader",
        "dict_loader",
        "babel_loader",
    ],
)
def test_get_locales(request: FixtureRequest, loader_fixture_name: str):
    loader = request.getfixturevalue(loader_fixture_name)

    locales = loader.locales
    assert len(locales) >= 2
    for locale in ("en_US", "de_DE"):
        assert locale in locales


@pytest.mark.parametrize(
    "loader_fixture_name",
    [
        "json_loader",
        "dict_loader",
        "babel_loader",
    ],
)
def test_translation(request: FixtureRequest, loader_fixture_name: str):
    loader = request.getfixturevalue(loader_fixture_name)

    assert loader.gettext("field required", "en_US") == "field required"
    assert loader.gettext("field required", "de_DE") == "Feld erforderlich"


@pytest.mark.parametrize(
    "loader_fixture_name",
    [
        "json_loader",
        "dict_loader",
        "babel_loader",
    ],
)
def test_unsupported_locale(request: FixtureRequest, loader_fixture_name: str):
    loader = request.getfixturevalue(loader_fixture_name)

    locale = "fr_FR"

    with pytest.raises(ValueError) as e:
        loader.gettext("field required", locale)

    assert str(e.value) == f"Locale '{locale}' wasn't found."


@pytest.mark.parametrize(
    "loader_fixture_name",
    [
        "json_loader",
        "dict_loader",
        "babel_loader",
    ],
)
def test_unknown_key(request: FixtureRequest, loader_fixture_name: str):
    loader = request.getfixturevalue(loader_fixture_name)

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
