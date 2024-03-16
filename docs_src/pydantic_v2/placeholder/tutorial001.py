from decimal import Decimal

from pydantic import BaseModel, ValidationError, Field
from pydantic_i18n import PydanticI18n


translations = {
    "en_US": {
        "Decimal input should have no more than {} in total":
            "Decimal input should have no more than {} in total",
    },
    "es_AR": {
        "Decimal input should have no more than {} in total":
            "La entrada decimal no debe tener más de {} en total",
    },
}

tr = PydanticI18n(translations)


class CoolSchema(BaseModel):
    my_field: Decimal = Field(max_digits=3)


try:
    CoolSchema(my_field=1111)
except ValidationError as e:
    translated_errors = tr.translate(e.errors(), locale="es_AR")

print(translated_errors)
# [
#     {
#         'type': 'decimal_max_digits',
#         'loc': ('my_field',),
#         'msg': 'La entrada decimal no debe tener más de 3 digits en total',
#         'input': 1111,
#         'ctx': {
#             'max_digits': 3
#         },
#         'url': 'https://errors.pydantic.dev/2.6/v/decimal_max_digits'
#     }
# ]
