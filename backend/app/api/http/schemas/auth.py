from pydantic import BaseModel


class RegisterRequest(BaseModel):
    email: str
    password: str


class RegisterResponse(BaseModel):
    message: str
