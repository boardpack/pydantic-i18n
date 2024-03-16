from pydantic import BaseModel, ValidationError
from pydantic_i18n import PydanticI18n, JsonLoader

loader = JsonLoader("./translations")
tr = PydanticI18n(loader)


class User(BaseModel):
    name: str


try:
    User()
except ValidationError as e:
    translated_errors = tr.translate(e.errors(), locale="de_DE")

print(translated_errors)
# [
#     {
#         'type': 'missing',
#         'loc': ('name',
#                 ),
#         'msg': 'Feld erforderlich',
#         'input': {
#
#         },
#         'url': 'https://errors.pydantic.dev/2.6/v/missing'
#     }
# ]
