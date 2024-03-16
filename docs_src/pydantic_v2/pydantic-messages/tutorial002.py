from pydantic_i18n import PydanticI18n

print(PydanticI18n.get_pydantic_messages(output="json"))
# {
#     "Field required": "Field required",
#     "Field is frozen": "Field is frozen",
#     "Error extracting attribute: {}": "Error extracting attribute: {}",
#     .....
# }

print(PydanticI18n.get_pydantic_messages(output="babel"))
# msgid "Field required"
# msgstr "Field required"
#
# msgid "Field is frozen"
# msgstr "Field is frozen"
#
# msgid "Error extracting attribute: {}"
# msgstr "Error extracting attribute: {}"
# ....
