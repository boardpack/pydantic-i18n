import os

import pytest

from pydantic_i18n import BabelLoader


@pytest.fixture
def babel_translations_directory() -> str:
    return os.path.abspath("./tests/translations/babel")


@pytest.fixture
def babel_loader(babel_translations_directory: str) -> BabelLoader:
    return BabelLoader(babel_translations_directory)
