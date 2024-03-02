import json
import re
from typing import TYPE_CHECKING, Callable, Dict, List, Pattern, Sequence, Union, cast

from .loaders import BaseLoader, DictLoader

if TYPE_CHECKING:  # pragma: no cover
    from pydantic.error_wrappers import ErrorDict

__all__ = ("PydanticI18n",)


class PydanticI18n:
    def __init__(
        self,
        source: Union[Dict[str, Dict[str, str]], BaseLoader],
        default_locale: str = "en_US",
    ):
        if isinstance(source, dict):
            source = DictLoader(source)

        self.source = source
        self.default_locale = default_locale
        self._pattern = self._init_pattern()

    def _init_pattern(self) -> Pattern[str]:
        keys = list(self.source.get_translations(self.default_locale))
        return re.compile(
            "|".join("({})".format(re.escape(i).replace(r"\{\}", "(.+)")) for i in keys)
        )

    def _translate(self, message: str, locale: str) -> str:
        placeholder_values = []
        placeholder_indexes = []
        searched = self._pattern.search(message)

        if searched:
            for group_index in range(len(searched.groups())):
                group_index += 1
                start = searched.start(group_index)
                end = searched.end(group_index)

                if start != end and not (start == 0 and end == len(message)):
                    placeholder_indexes.append((start, end))
                    placeholder_values.append(searched.group(group_index))

        key = ""
        prev = 0
        for start, end in placeholder_indexes:
            key += message[prev:start] + "{}"
            prev = end
        key += message[prev:]

        return self.source.gettext(key, locale).format(*placeholder_values)

    @property
    def locales(self) -> Sequence[str]:
        return self.source.locales

    def translate(
        self,
        errors: List["ErrorDict"],
        locale: str,
    ) -> List["ErrorDict"]:
        return [
            cast(
                "ErrorDict",
                {
                    **error,
                    "msg": self._translate(error["msg"], locale),
                },
            )
            for error in errors
        ]

    @classmethod
    def get_pydantic_messages(cls, output: str = "dict") -> Union[Dict[str, str], str]:
        output_mapping: Dict[str, Callable[[], Union[Dict[str, str], str]]] = {
            "json": cls._get_pydantic_messages_json,
            "dict": cls._get_pydantic_messages_dict,
            "babel": cls._get_pydantic_messages_babel,
        }

        return output_mapping[output]()

    @classmethod
    def _get_pydantic_messages_dict(cls) -> Dict[str, str]:
        try:
            from pydantic.v1 import errors
        except ImportError:  # pragma: no cover
            from pydantic import errors  # type: ignore[no-redef]

        messages = (
            re.sub(r"\{.+\}", "{}", getattr(errors, name).msg_template)
            for name in errors.__all__
            if hasattr(getattr(errors, name), "msg_template")
        )
        return {value: value for value in messages}

    @classmethod
    def _get_pydantic_messages_json(cls) -> str:
        return json.dumps(cls._get_pydantic_messages_dict(), indent=4)

    @classmethod
    def _get_pydantic_messages_babel(cls) -> str:
        return "\n\n".join(
            f'msgid "{item}"\nmsgstr "{item}"'
            for item in cls._get_pydantic_messages_dict()
        )
