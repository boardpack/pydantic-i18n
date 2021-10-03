import json
import re
from typing import Dict

import pytest

from pydantic_i18n import PydanticI18n


@pytest.fixture
def json_output() -> Dict[str, str]:
    output = PydanticI18n.get_pydantic_messages(output="json")
    assert isinstance(output, str)

    return json.loads(output)


@pytest.fixture
def dict_output() -> Dict[str, str]:
    output = PydanticI18n.get_pydantic_messages(output="dict")
    assert isinstance(output, dict)

    return output


@pytest.fixture
def babel_output() -> Dict[str, str]:
    output = PydanticI18n.get_pydantic_messages(output="babel")
    assert isinstance(output, str)

    return dict(
        zip(
            re.findall('msgid "(.+)"\n', output),
            re.findall('msgstr "(.+)"\n', output),
        )
    )


@pytest.mark.parametrize(
    "output",
    [
        pytest.lazy_fixture("json_output"),
        pytest.lazy_fixture("dict_output"),
        pytest.lazy_fixture("babel_output"),
    ],
)
def test_messages(output: Dict[str, str]) -> None:
    for k, v in output.items():
        assert isinstance(k, str)
        assert k == v


def test_dict_by_default():
    output = PydanticI18n.get_pydantic_messages()
    assert isinstance(output, dict)


@pytest.mark.parametrize(
    "output",
    [
        pytest.lazy_fixture("json_output"),
        pytest.lazy_fixture("dict_output"),
        pytest.lazy_fixture("babel_output"),
    ],
)
def test_placeholders_dict(output: Dict[str, str]):
    for k in output:
        if "{" in k:
            assert "{}" in k
