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
#         'loc': ('name',),
#         'msg': 'Feld erforderlich',
#         'type': 'value_error.missing'
#     }
# ]
