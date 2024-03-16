from pydantic import BaseModel, ValidationError
from pydantic_i18n import PydanticI18n


translations = {
    "en_US": {
        "Field required": "field required",
    },
    "de_DE": {
        "Field required": "Feld erforderlich",
    },
}

tr = PydanticI18n(translations)


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
#         'loc': ('name',),
#         'msg': 'Feld erforderlich',
#         'input': {
#
#         },
#         'url': 'https://errors.pydantic.dev/2.6/v/missing'
#     }
# ]
