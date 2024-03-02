"""pydantic-i18n is an extension to support an i18n for the pydantic error messages."""

__author__ = """Roman Sadzhenytsia"""
__email__ = "urchin.dukkee@gmail.com"
__version__ = "0.4.1"

from .loaders import BabelLoader, BaseLoader, DictLoader, JsonLoader
from .main import PydanticI18n

__all__ = (
    "PydanticI18n",
    "BaseLoader",
    "BabelLoader",
    "DictLoader",
    "JsonLoader",
)
