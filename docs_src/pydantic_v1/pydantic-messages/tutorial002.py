from pydantic_i18n import PydanticI18n

print(PydanticI18n.get_pydantic_messages(output="json"))
# {
#     "field required": "field required",
#     "extra fields not permitted": "extra fields not permitted",
#     "none is not an allowed value": "none is not an allowed value",
#     .....
# }

print(PydanticI18n.get_pydantic_messages(output="babel"))
# msgid "field required"
# msgstr "field required"
#
# msgid "extra fields not permitted"
# msgstr "extra fields not permitted"
#
# msgid "none is not an allowed value"
# msgstr "none is not an allowed value"
# ....
