import httpx
from typing_extensions import Literal, TypedDict

from httpx_oauth.errors import GetProfileError
from httpx_oauth.oauth2 import BaseOAuth2

AUTHORIZE_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
ACCESS_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
REVOKE_TOKEN_ENDPOINT = "https://accounts.google.com/o/oauth2/revoke"
BASE_SCOPES = [
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
]
PROFILE_FIELDS = ["names", "emailAddresses", "photos"]
PROFILE_ENDPOINT = "https://people.googleapis.com/v1/people/me"


class GoogleOAuth2AuthorizeParams(TypedDict, total=False):
    access_type: Literal["online", "offline"]
    include_granted_scopes: bool
    login_hint: str
    prompt: Literal["none", "consent", "select_account"]


class GoogleOAuth2(BaseOAuth2[GoogleOAuth2AuthorizeParams]):
    def __init__(self, client_id: str, client_secret: str, name="google"):
        super().__init__(
            client_id,
            client_secret,
            AUTHORIZE_ENDPOINT,
            ACCESS_TOKEN_ENDPOINT,
            ACCESS_TOKEN_ENDPOINT,
            REVOKE_TOKEN_ENDPOINT,
            name=name,
            base_scopes=BASE_SCOPES,
        )

    async def get_profile(self, token: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                PROFILE_ENDPOINT,
                params={"personFields": ",".join(PROFILE_FIELDS), "key": token},
            )

            if response.status_code >= 400:
                raise GetProfileError(response.json())

            return response.json()