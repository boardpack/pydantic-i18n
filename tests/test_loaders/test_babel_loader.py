from pydantic_i18n import BabelLoader


def test_init(babel_translations_directory: str):
    babel_loader = BabelLoader(babel_translations_directory)
    assert len(babel_loader.translations) >= 2
