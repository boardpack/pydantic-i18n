import json
import re
from typing import Dict

import pytest
from _pytest.fixtures import FixtureRequest

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
    "output_fixture_name",
    [
        "json_output",
        "dict_output",
        "babel_output",
    ],
)
def test_messages(request: FixtureRequest, output_fixture_name: str) -> None:
    output = request.getfixturevalue(output_fixture_name)

    for k, v in output.items():
        assert isinstance(k, str)
        assert k == v


def test_dict_by_default():
    output = PydanticI18n.get_pydantic_messages()
    assert isinstance(output, dict)


@pytest.mark.parametrize(
    "output_fixture_name",
    [
        "json_output",
        "dict_output",
        "babel_output",
    ],
)
def test_placeholders_dict(request: FixtureRequest, output_fixture_name: str) -> None:
    output = request.getfixturevalue(output_fixture_name)

    for k in output:
        if "{" in k:
            assert "{}" in k
