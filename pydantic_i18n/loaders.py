import json
import os
from typing import Dict, Mapping, Sequence

__all__ = (
    "BaseLoader",
    "BabelLoader",
    "DictLoader",
    "JsonLoader",
)


class BaseLoader:
    @property
    def locales(self) -> Sequence[str]:
        raise NotImplementedError

    def get_translations(self, locale: str) -> Mapping[str, str]:
        raise NotImplementedError

    def gettext(self, key: str, locale: str) -> str:
        if locale not in self.locales:
            raise ValueError(f"Locale '{locale}' wasn't found.")

        data = self.get_translations(locale)
        return data.get(key, key)


class DictLoader(BaseLoader):
    def __init__(self, translations: Dict[str, Dict[str, str]]):
        self.data = translations

    @property
    def locales(self) -> Sequence[str]:
        locales: Sequence[str] = tuple(self.data.keys())
        return locales

    def get_translations(self, locale: str) -> Mapping[str, str]:
        return self.data[locale]


class JsonLoader(BaseLoader):
    def __init__(self, directory: str):
        if not os.path.exists(directory):
            raise OSError(f"Directory '{directory}' doesn't exist.")
        if not os.path.isdir(directory):
            raise OSError(f"'{directory}' is not a directory.")

        self.directory = directory

    @property
    def locales(self) -> Sequence[str]:
        locales: Sequence[str] = [
            filename[:-5]
            for filename in os.listdir(self.directory)
            if filename.endswith(".json")
        ]
        return locales

    def get_translations(self, locale: str) -> Mapping[str, str]:
        with open(os.path.join(self.directory, f"{locale}.json")) as fp:
            data: Dict[str, str] = json.load(fp)

        return data


class BabelLoader(BaseLoader):
    def __init__(self, translations_directory: str):
        try:
            from babel import Locale
            from babel.support import Translations
        except ImportError as e:  # pragma: no cover
            raise ImportError(
                "babel not installed, you cannot use this loader.\n"
                "To install, run: pip install babel"
            ) from e

        self.translations = {}

        for dir_name in os.listdir(translations_directory):
            locale = Locale.parse(dir_name)
            self.translations[str(locale)] = Translations.load(
                translations_directory, [locale]
            )

    @property
    def locales(self) -> Sequence[str]:
        return tuple(self.translations)

    def get_translations(self, locale: str) -> Dict[str, str]:
        return {k: v for k, v in self.translations[locale]._catalog.items() if k}  # type: ignore
