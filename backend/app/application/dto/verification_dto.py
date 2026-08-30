from pydantic import BaseModel, EmailStr, Field


class VerifyEmailRequest(BaseModel):
    code: str = Field(min_length=6, max_length=6)


class MessageResponse(BaseModel):
    message: str


class ConfirmAccountDeletionRequest(BaseModel):
    code: str = Field(min_length=6, max_length=6)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6)
    new_password: str = Field(min_length=8, max_length=128)
