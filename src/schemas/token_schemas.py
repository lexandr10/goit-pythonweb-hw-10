from pydantic import BaseModel



class TokenResponseSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str


class RefreshTokenResponseSchema(BaseModel):
    refresh_token: str