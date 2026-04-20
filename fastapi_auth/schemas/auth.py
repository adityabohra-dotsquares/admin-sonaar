from pydantic import BaseModel, validator


class UserSignup(BaseModel):
    email: str
    # username: str
    password: str
    password2: str
    recaptcha_token: str
    mailing_list: bool = False

    @validator("password2")
    def passwords_match(cls, v, values):
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v


class UserLogin(BaseModel):
    email: str
    password: str
    remember_me: bool = False
    recaptcha_token: str


class RefreshToken(BaseModel):
    refresh_token: str


class ForgotPasswordSchema(BaseModel):
    email_address: str


class ResetPasswordSchema(BaseModel):
    key: str
    password1: str
    password2: str


class ChangePassword(BaseModel):
    current_password: str
    new_password: str


class ResendVerificationSchema(BaseModel):
    email: str

class GoogleLoginSchema(BaseModel):
    access_token: str

    @validator("access_token")
    def token_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Access token cannot be empty")
        return v
