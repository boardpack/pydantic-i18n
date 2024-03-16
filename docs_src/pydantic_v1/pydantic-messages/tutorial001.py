from pydantic_i18n import PydanticI18n

print(PydanticI18n.get_pydantic_messages())
# {
#     "field required": "field required",
#     "extra fields not permitted": "extra fields not permitted",
#     "none is not an allowed value": "none is not an allowed value",
#     "value is not none": "value is not none",
#     "value could not be parsed to a boolean": "value could not be parsed to a boolean",
#     "byte type expected": "byte type expected",
#     .....
# }
