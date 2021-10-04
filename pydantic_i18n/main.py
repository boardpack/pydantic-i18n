import json
import re
from typing import Any, Callable, Dict, List, Pattern, Sequence, Union

from .loaders import BaseLoader, DictLoader

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
            "|".join("({})".format(i.replace("{}", "(.+)")) for i in keys)
        )

    def _translate(self, message: str, locale: str) -> str:
        key = message
        placeholder = self._pattern.search(message) or ""

        if placeholder:
            index = placeholder.groups().index(message) + 1  # type: ignore
            placeholder = placeholder.groups()[index] or ""  # type: ignore

            if placeholder and key != placeholder:
                key = key.replace(placeholder, "{}")

        return self.source.gettext(key, locale).replace("{}", placeholder)

    @property
    def locales(self) -> Sequence[str]:
        return self.source.locales

    def translate(
        self,
        errors: List[Dict[str, Any]],
        locale: str,
    ) -> List[Dict[str, Any]]:
        return [
            {
                **error,
                "msg": self._translate(error["msg"], locale),
            }
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
        from pydantic import errors

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
