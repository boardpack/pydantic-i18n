from pydantic import BaseModel, ValidationError
from pydantic_i18n import PydanticI18n


translations = {
    "en_US": {
        "field required": "field required",
    },
    "de_DE": {
        "field required": "Feld erforderlich",
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
#         'loc': ('name',),
#         'msg': 'Feld erforderlich',
#         'type': 'value_error.missing'
#     }
# ]
