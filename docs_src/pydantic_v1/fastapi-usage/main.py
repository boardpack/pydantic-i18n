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
