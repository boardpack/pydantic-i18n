import json
from typing import Any, Callable, Dict, List, Sequence, Union

from .loaders import BaseLoader, DictLoader

__all__ = ("PydanticI18n",)


class PydanticI18n:
    def __init__(self, source: Union[Dict[str, Dict[str, str]], BaseLoader]):
        if isinstance(source, dict):
            source = DictLoader(source)

        self.source = source

    @property
    def locales(self) -> Sequence[str]:
        return self.source.locales

    def translate(
        self,
        errors: List[Dict[str, Any]],
        locale: str = "en",
    ) -> List[Dict[str, Any]]:
        return [
            {
                **error,
                "msg": self.source.gettext(error["msg"], locale),
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
            getattr(errors, name).msg_template
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
