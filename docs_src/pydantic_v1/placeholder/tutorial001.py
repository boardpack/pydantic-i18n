from enum import Enum

from pydantic import BaseModel, ValidationError
from pydantic_i18n import PydanticI18n


translations = {
    "en_US": {
        "value is not a valid enumeration member; permitted: {}":
            "value is not a valid enumeration member; permitted: {}",
    },
    "es_AR": {
        "value is not a valid enumeration member; permitted: {}":
            "el valor no es uno de los valores permitidos, que son: {}",
    },
}

tr = PydanticI18n(translations)


class ACoolEnum(Enum):
    NINE_TO_TWELVE = "9_to_12"
    TWELVE_TO_FIFTEEN = "12_to_15"
    FOURTEEN_TO_EIGHTEEN = "14_to_18"


class CoolSchema(BaseModel):
    enum_field: ACoolEnum


try:
    CoolSchema(enum_field="invalid value")
except ValidationError as e:
    translated_errors = tr.translate(e.errors(), locale="es_AR")

print(translated_errors)
# [
#     {
#         'ctx': {
#             'enum_values': [
#                 <ACoolEnum.NINE_TO_TWELVE: '9_to_12'>,
#                 <ACoolEnum.TWELVE_TO_FIFTEEN: '12_to_15'>,
#                 <ACoolEnum.FOURTEEN_TO_EIGHTEEN: '14_to_18'>
#             ]
#         },
#         'loc': ('enum_field',),
#         'msg': "el valor no es uno de los valores permitidos, que son: '9_to_12', '12_to_15', '14_to_18'",
#         'type': 'type_error.enum'
#     }
# ]
