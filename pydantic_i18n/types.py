import re
from typing import Any, Mapping, Optional


class RegexDict(dict):
    def __getitem__(self, item: str):
        for k, v in self.items():
            if re.match(k, item):
                return v
        raise KeyError(item)

    def get(self, key: str, default: Optional[Any] = None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default


class BabelRegex(RegexDict):
    def __init__(self, mapping: Mapping[str, Any] = None, /, **kwargs):
        if mapping is not None:
            mapping = {
                "{}".format(key.replace("{}", "(.+)")): value
                for key, value in mapping.items()
            }
        else:
            mapping = {}
        if kwargs:
            mapping.update(
                {
                    "{}".format(key.replace("{}", "(.+)")): value
                    for key, value in kwargs.items()
                }
            )
        super(BabelRegex, self).__init__(mapping)

    def __setitem__(self, key, value):
        super(BabelRegex, self).__setitem__(self.expression(key), value)

    @classmethod
    def expression(cls, key: str):
        return "{}".format(key.replace("{}", "(.+)"))
