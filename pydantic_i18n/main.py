import json
import re
from locale import normalize
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Pattern, Sequence, Union
from urllib.parse import urlparse

from .loaders import BaseLoader, DictLoader

if TYPE_CHECKING:  # pragma: no cover
    from pydantic.error_wrappers import ErrorDict

__all__ = ("PydanticI18n",)


class PydanticI18n:
    language_code_re = re.compile(
        r"^[a-z]{1,8}(?:-[a-z0-9]{1,8})*(?:@[a-z0-9]{1,20})?$", re.IGNORECASE
    )
    language_code_prefix_re = re.compile(r"^/(\w+([@-]\w+){0,2})(/|$)")

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
        placeholder = ""
        searched = self._pattern.search(message)

        if searched:
            groups = searched.groups()
            index = groups.index(message)

            if len(groups) > index + 1:
                placeholder = groups[index + 1]
            elif len(groups) > index:
                placeholder = groups[index]

            placeholder = placeholder or ""
            if placeholder and key != placeholder:
                key = key.replace(placeholder, "{}")

        return self.source.gettext(key, locale).replace("{}", placeholder)

    @property
    def locales(self) -> Sequence[str]:
        return self.source.locales

    def translate(
        self,
        errors: List["ErrorDict"],
        locale: str,
    ) -> List["ErrorDict"]:
        return [
            {
                **error,  # type: ignore
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

    @classmethod
    def get_locale_from_request(
        cls,
        url: Union[str, None] = None,
        headers: Union[Dict[str, Any], None] = None,
        default: Union[str, None] = None,
    ) -> Union[str, None]:
        lang = ""

        if url:
            parsed = urlparse(url)

            if parsed.netloc.count(".") > 1:
                lang = parsed.netloc.split(".")[0]
            else:
                result = cls.language_code_prefix_re.search(parsed.path)
                if result:
                    lang = result.group(1)

        if headers:
            lang = (
                headers.get("Accept-Language") or headers.get("accept-language") or ""
            )

        if not cls.language_code_re.search(lang):
            return default

        lang = lang.lower()
        if "-" in lang:
            lang = lang.replace("-", "_")

        locale = normalize(lang).split(".")[0]
        if locale == lang:
            return default  # assume that lang was incorrect, e.g. es2

        return locale
