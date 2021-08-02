import pytest

from pydantic_i18n import JsonLoader


def test_init(json_translations_directory: str):
    json_loader = JsonLoader(json_translations_directory)
    assert json_loader.directory == json_translations_directory


def test_not_dir_path(tmp_path):
    fp = tmp_path / "hello.txt"
    fp.touch()

    with pytest.raises(OSError) as excinfo:
        JsonLoader(str(fp))

    assert str(excinfo.value) == f"'{str(fp)}' is not a directory."
