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

        # NOTE: If we have placeholder values in the input text, we assume the
        # translated texts have the correct number of placeholders in the target
        # language. If we have too many placeholder values, Python will ignore
        # them. If we have too few, we have to handle the `IndexError` (and return
        # the un-translated text to be on the safe side).
        message_translated = self.source.gettext(key, locale)
        # NOTE: If there are no placeholder_values, we not only can but must skip
        # formatting in the off-chance that the message contains format characters {
        # or } (especially if the lookup above failed and we use the un-translated
        # message)
        if placeholder_values:
            message_translated = message_translated.format(*placeholder_values)
        return message_translated

    @property
    def locales(self) -> Sequence[str]:
        return self.source.locales

    def translate(
        self,
        errors: List["ErrorDict"],
        locale: str,
        type_search: bool = False,
    ) -> List["ErrorDict"]:
        result = []

        for error in errors:
            message = error["msg"]
            error_type = error.get("type")

            translated_message = self._translate(message, locale)
            if type_search and error_type and translated_message == message:
                translated_message = self._translate(error_type, locale)
                if translated_message == error_type:
                    translated_message = message

            result.append(
                cast(
                    "ErrorDict",
                    {
                        **error,
                        "msg": translated_message,
                    },
                )
            )

        return result

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
            from pydantic_core._pydantic_core import list_all_errors
        except ImportError:  # pragma: no cover
            from pydantic import errors

            list_all_errors = None  # type: ignore

        if list_all_errors is not None:
            messages = [item["message_template_python"] for item in list_all_errors()]
        else:
            messages = (
                getattr(errors, name).msg_template
                for name in errors.__all__
                if hasattr(getattr(errors, name), "msg_template")
            )

        return {
            value: value
            for value in (re.sub(r"\{.+\}", "{}", item) for item in messages)
            if value != "{}"
        }

    @classmethod
    def _get_pydantic_messages_json(cls) -> str:
        return json.dumps(cls._get_pydantic_messages_dict(), indent=4)

    @classmethod
    def _get_pydantic_messages_babel(cls) -> str:
        return "\n\n".join(
            f'msgid "{item}"\nmsgstr "{item}"'
            for item in cls._get_pydantic_messages_dict()
        )
