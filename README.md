<p align="center">
  <a href="https://pydantic-i18n.boardpack.org/"><img src="https://pydantic-i18n.boardpack.org/img/logo-white.png" alt="pydantic-i18n"></a>
</p>
<p align="center">
    <em>pydantic-i18n is an extension to support an i18n for the pydantic error messages.</em>
</p>
<p align="center">
    <a href="https://github.com/boardpack/pydantic-i18n/actions?query=workflow%3ATest" target="_blank">
        <img src="https://github.com/boardpack/pydantic-i18n/workflows/Test/badge.svg" alt="Test">
    </a>
    <a href="https://codecov.io/gh/boardpack/pydantic-i18n" target="_blank">
        <img src="https://img.shields.io/codecov/c/github/boardpack/pydantic-i18n?color=%2334D058" alt="Coverage">
    </a>
    <a href="https://pypi.org/project/pydantic-i18n" target="_blank">
        <img src="https://img.shields.io/pypi/v/pydantic-i18n?color=%2334D058&label=pypi%20package" alt="Package version">
    </a>
    <a href="https://github.com/psf/black"><img alt="Code style: black" src="https://camo.githubusercontent.com/d91ed7ac7abbd5a6102cbe988dd8e9ac21bde0a73d97be7603b891ad08ce3479/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f636f64652532307374796c652d626c61636b2d3030303030302e737667" data-canonical-src="https://img.shields.io/badge/code%20style-black-000000.svg" style="max-width:100%;"></a>
    <a href="https://pycqa.github.io/isort/" rel="nofollow"><img src="https://camo.githubusercontent.com/fe4a658dd745f746410f961ae45d44355db1cc0e4c09c7877d265c1380248943/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f253230696d706f7274732d69736f72742d2532333136373462313f7374796c653d666c6174266c6162656c436f6c6f723d656638333336" alt="Imports: isort" data-canonical-src="https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&amp;labelColor=ef8336" style="max-width:100%;"></a>
</p>

---

**Documentation**: <a href="https://pydantic-i18n.boardpack.org" target="_blank">https://pydantic-i18n.boardpack.org</a>

**Source Code**: <a href="https://github.com/boardpack/pydantic-i18n" target="_blank">https://github.com/boardpack/pydantic-i18n</a>

---

## Requirements

Python 3.8+

pydantic-i18n has the next dependencies:

* <a href="https://pydantic-docs.helpmanual.io/" class="external-link" target="_blank">Pydantic</a>
* <a href="http://babel.pocoo.org/en/latest/index.html" class="external-link" target="_blank">Babel</a>


## Installation

<div class="termy">

```console
$ pip install pydantic-i18n

---> 100%
```

</div>

## First steps

To start to work with pydantic-i18n, you can just create a dictionary (or
create any needed translations storage and then convert it into dictionary)
and pass to the main `PydanticI18n` class.

To translate messages, you need to pass result of `exception.errors()` call to
the `translate` method:

```Python  hl_lines="14 24"
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
```
_(This script is complete, it should run "as is")_

In the next chapters, you will see current available loaders and how to
implement your own loader.

## Usage with FastAPI

Here is a simple example usage with FastAPI.

### Create it

Let's create a `tr.py` file:

```Python linenums="1" hl_lines="13-22 25-26 32 35"
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from pydantic_i18n import PydanticI18n

__all__ = ["get_locale", "validation_exception_handler"]


DEFAULT_LOCALE = "en_US"

translations = {
    "en_US": {
        "field required": "field required",
    },
    "de_DE": {
        "field required": "Feld erforderlich",
    },
}

tr = PydanticI18n(translations)


def get_locale(locale: str = DEFAULT_LOCALE) -> str:
    return locale


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    current_locale = request.query_params.get("locale", DEFAULT_LOCALE)
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": tr.translate(exc.errors(), current_locale)},
    )
```

`11-20`: As you see, we selected the simplest variant to store translations,
you can use any that you need.

`23-24`: To not include `locale` query parameter into every handler, we
created a simple function `get_locale`, which we will include as a global
dependency with `Depends`.

`29-36`: An example of overridden function to return translated messages of the
validation exception.

Now we are ready to create a FastAPI application:

```Python linenums="1" hl_lines="8 10"
from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError

from pydantic import BaseModel

import tr

app = FastAPI(dependencies=[Depends(tr.get_locale)])

app.add_exception_handler(RequestValidationError, tr.validation_exception_handler)


class User(BaseModel):
    name: str


@app.post("/user", response_model=User)
def create_user(request: Request, user: User):
    pass
```

`8`: Add `get_locale` function as a global dependency.

!!! note
    If you need to use i18n only for specific part of your
    application, you can add this `get_locale` function to the specific
    `APIRouter`. More information about `APIRouter` you can find
    [here](https://fastapi.tiangolo.com/tutorial/bigger-applications/#apirouter).

`10`: Override default request validation error handler with
`validation_exception_handler`.

### Run it

Run the server with:

<div class="termy">

```console
$ uvicorn main:app --reload

INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [28720]
INFO:     Started server process [28722]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

</div>

<details markdown="1">
<summary>About the command <code>uvicorn main:app --reload</code>...</summary>

The command `uvicorn main:app` refers to:

* `main`: the file `main.py` (the Python "module").
* `app`: the object created inside of `main.py` with the line `app = FastAPI()`.
* `--reload`: make the server restart after code changes. Only do this for development.

</details>

### Send it

Open your browser at <a href="http://127.0.0.1:8000/docs#/default/create_user_user_post" class="external-link" target="_blank">http://127.0.0.1:8000/docs#/default/create_user_user_post</a>.

Send POST-request with empty body and `de_DE` locale query param via swagger UI
 or `curl`:

```bash
$ curl -X 'POST' \
  'http://127.0.0.1:8000/user?locale=de_DE' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
}'
```

### Check it

As a result, you will get the next response body:

```json hl_lines="8"
{
  "detail": [
    {
      "loc": [
        "body",
        "name"
      ],
      "msg": "Feld erforderlich",
      "type": "value_error.missing"
    }
  ]
}
```

If you don't mention the `locale` param, English locale will be used by
default.

## Get current error strings from Pydantic

pydantic-i18n doesn't provide prepared translations of all current error
messages from pydantic, but you can use a special class method
`PydanticI18n.get_pydantic_messages` to load original messages in English. By
default, it returns a `dict` object:

```Python
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
```
_(This script is complete, it should run "as is")_

You can also choose JSON string or Babel format with `output` parameter values
`"json"` and `"babel"`:

```Python
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

```
_(This script is complete, it should run "as is")_


## Loaders

pydantic-i18n provides a list of loaders to use translations.

### DictLoader

DictLoader is the simplest loader and default in PydanticI18n. So you can
just pass your translations dictionary without any other preparation steps.

```Python
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
```
_(This script is complete, it should run "as is")_

### JsonLoader

JsonLoader needs to get the path to some directory with the next structure:

```text

|-- translations
    |-- en_US.json
    |-- de_DE.json
    |-- ...
```

where e.g. `en_US.json` looks like:

```json
{
    "field required": "field required"
}
```

and `de_DE.json`:

```json
{
    "field required": "Feld erforderlich"
}
```

Then we can use `JsonLoader` to load our translations:

```Python
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

```
_(This script is complete, it should run "as is")_

### BabelLoader

BabelLoader works in the similar way as JsonLoader. It also needs a
translations directory with the next structure:

```text

|-- translations
    |-- en_US
        |-- LC_MESSAGES
            |-- messages.mo
            |-- messages.po
    |-- de_DE
        |-- LC_MESSAGES
            |-- messages.mo
            |-- messages.po
    |-- ...
```

Information about translations preparation you can find on the
[Babel docs pages](http://babel.pocoo.org/en/latest/cmdline.html){:target="_blank"} and e.g.
from [this article](https://phrase.com/blog/posts/i18n-advantages-babel-python/#Message_Extraction){:target="_blank"}.

Here is an example of the `BabelLoader` usage:

```Python
from pydantic import BaseModel, ValidationError
from pydantic_i18n import PydanticI18n, BabelLoader

loader = BabelLoader("./translations")
tr = PydanticI18n(loader)


class User(BaseModel):
    name: str


try:
    User()
except ValidationError as e:
    translated_errors = tr.translate(e.errors(), locale="de")

print(translated_errors)
# [
#     {
#         'loc': ('name',),
#         'msg': 'Feld erforderlich',
#         'type': 'value_error.missing'
#     }
# ]

```
_(This script is complete, it should run "as is")_

### Write your own loader

If current loaders aren't suitable for you, it's possible to write your own
loader and use it with pydantic-i18n. To do it, you need to import
`BaseLoader` and implement the next items:

 - property `locales` to get a list of locales;
 - method `get_translations` to get content for the specific locale.

In some cases you will also need to change implementation of the `gettext`
method.

Here is an example of the loader to get translations from CSV files:

```text
|-- translations
    |-- en_US.csv
    |-- de_DE.csv
    |-- ...
```

`en_US.csv` content:

```csv
field required,field required
```

`de_DE.csv` content:

```csv
field required,Feld erforderlich
```

```Python
import os
from typing import List, Dict

from pydantic import BaseModel, ValidationError
from pydantic_i18n import PydanticI18n, BaseLoader


class CsvLoader(BaseLoader):
    def __init__(self, directory: str):
        self.directory = directory

    @property
    def locales(self) -> List[str]:
        return [
            filename[:-4]
            for filename in os.listdir(self.directory)
            if filename.endswith(".csv")
        ]

    def get_translations(self, locale: str) -> Dict[str, str]:
        with open(os.path.join(self.directory, f"{locale}.csv")) as fp:
            data = dict(line.strip().split(",") for line in fp)

        return data


class User(BaseModel):
    name: str


if __name__ == '__main__':
    loader = CsvLoader("./translations")
    tr = PydanticI18n(loader)

    try:
        User()
    except ValidationError as e:
        translated_errors = tr.translate(e.errors(), locale="de")

    print(translated_errors)
    # [
    #     {
    #         'loc': ('name',),
    #         'msg': 'Feld erforderlich',
    #         'type': 'value_error.missing'
    #     }
    # ]

```
_(This script is complete, it should run "as is")_

## Acknowledgments

Thanks to [Samuel Colvin](https://github.com/samuelcolvin) and his
[pydantic](https://github.com/samuelcolvin/pydantic) library.

Also, thanks to [Sebastián Ramírez](https://github.com/tiangolo) and his
[FastAPI](https://github.com/tiangolo/fastapi) project,  some scripts and
documentation structure and parts were used from there.

## License

This project is licensed under the terms of the MIT license.
