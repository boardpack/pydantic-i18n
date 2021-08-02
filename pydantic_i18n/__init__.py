"""Top-level package for pydantic-i18n."""

__author__ = """Roman Sadzhenytsia"""
__email__ = "urchin.dukkee@gmail.com"
__version__ = "0.1.0"

from .loaders import BabelLoader, BaseLoader, DictLoader, JsonLoader
from .main import PydanticI18n

__all__ = (
    "PydanticI18n",
    "BaseLoader",
    "BabelLoader",
    "DictLoader",
    "JsonLoader",
)
