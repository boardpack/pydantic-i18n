import os
from typing import List, Dict

from pydantic import BaseModel, ValidationError
from pydantic_i18n import PydanticI18n, BaseLoader


class CsvLoader(BaseLoader):
    def __init__(self, directory: str):
        self.directory = directory

    @property
    def locales(self) -> List[str]:
        return [
            filename[:-4]
            for filename in os.listdir(self.directory)
            if filename.endswith(".csv")
        ]

    def get_translations(self, locale: str) -> Dict[str, str]:
        with open(os.path.join(self.directory, f"{locale}.csv")) as fp:
            data = dict(line.strip().split(",") for line in fp)

        return data


class User(BaseModel):
    name: str


if __name__ == '__main__':
    loader = CsvLoader("./translations")
    tr = PydanticI18n(loader)

    try:
        User()
    except ValidationError as e:
        translated_errors = tr.translate(e.errors(), locale="de")

    print(translated_errors)
    # [
    #     {
    #         'loc': ('name',),
    #         'msg': 'Feld erforderlich',
    #         'type': 'value_error.missing'
    #     }
    # ]
