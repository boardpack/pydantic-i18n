from pydantic_i18n import PydanticI18n

print(PydanticI18n.get_pydantic_messages())
# {
#     "Object has no attribute '{}'": "Object has no attribute '{}'",
#     "Invalid JSON: {}": "Invalid JSON: {}",
#     "JSON input should be string, bytes or bytearray": "JSON input should be string, bytes or bytearray",
#     "Recursion error - cyclic reference detected": "Recursion error - cyclic reference detected",
#     "Field required": "Field required",
#     "Field is frozen": "Field is frozen",
#     .....
# }
