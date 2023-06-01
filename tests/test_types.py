import re
from string import Formatter

from pydantic_i18n.types import BabelRegex, RegexDict


def test_regex_dict_get():
    storage = RegexDict(
        {
            "value is not valid integer": "value is not valid integer",
            "address (.+) is not support": "address {} is not support",
            "image (.+) is not valid (.+) for (.+)": "image {} is not valid {} for {}",
        }
    )
    assert storage.get("address foo@bar.com is not support") is not None
    assert storage.get("image <object> is not valid object for bucket") is not None
    assert storage["address foo@bar.com is not support"] is not None
    assert storage["image <object> is not valid object for bucket"] is not None


def test_babel_regex_expression():
    storage = BabelRegex()

    exp1_input = "image {} is not valid {} for {}... {}...."
    exp1_output = "image (.+) is not valid (.+) for (.+)... (.+)...."

    exp2_input = "image not found"
    exp2_output = "image not found"

    assert storage.expression(exp1_input) == exp1_output
    assert storage.expression(exp2_input) == exp2_output


def test_babel_regex_insert_get():
    storage = BabelRegex(
        {
            "value is not valid integer": "value is not valid integer",
            "address {} is not support": "address {} is not support",
            "image {} is not valid {} for {}": "image {} is not valid {} for {}",
        }
    )
    storage["text {} in message not supported"] = "text {} in message not supported"

    assert storage.get("address foo@bar.com is not support") is not None
    assert storage.get("image <object> is not valid object for bucket") is not None
    assert storage.get("text ABC-102-120 in message not supported") is not None
    assert storage["address foo@bar.com is not support"] is not None
    assert storage["image <object> is not valid object for bucket"] is not None
    assert storage["text ABC-102-120 in message not supported"] is not None

    assert storage.get("type integer not found") is None
    assert storage.get("type integer not found", "Not Found") == "Not Found"


def test_babel_regex_parser():
    storage = BabelRegex(
        {
            "image {} is not valid {} for {}": "image {} is not valid {} for {}",
        }
    )
    error_message = "image foo.png is not valid mimetype for dev/null"

    error_pattern = storage.get(error_message)
    #
    error_pattern_expression = storage.expression(error_pattern)

    error_pattern_expression_compiled = re.compile(error_pattern_expression)
    match = re.match(pattern=error_pattern_expression_compiled, string=error_message)
    params = match.groups()
    assert params == ("foo.png", "mimetype", "dev/null")
    assert Formatter().format(error_pattern, *params) == error_message
