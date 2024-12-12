from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os
import oandapyV20  # type: ignore
import oandapyV20.endpoints.accounts as accounts  # type: ignore

load_dotenv()


class Config(BaseModel):
    account_id: str = Field(
        title="Account ID",
        description="The account ID used for connecting to OANDA and executing trades.",
        examples=["101-001-11111111-001"],
        default_factory=lambda: os.getenv("OANDA_PRACTICE_ACCOUNT_ID", ""),
    )

    access_token: str = Field(
        title="Access Token",
        description="The access token used for connecting to OANDA and executing trades.",
        examples=["a1b2c3d4e5f6g7h8i9j0"],
        default_factory=lambda: os.getenv("OANDA_PRACTICE_ACCESS_TOKEN", ""),
    )


class Galgoz(BaseModel):
    config: Config

    def __init__(self, use_live_account=False):
        account_id_env = (
            "OANDA_LIVE_ACCOUNT_ID" if use_live_account else "OANDA_PRACTICE_ACCOUNT_ID"
        )
        access_token_env = (
            "OANDA_LIVE_ACCESS_TOKEN"
            if use_live_account
            else "OANDA_PRACTICE_ACCESS_TOKEN"
        )

        config_data = {
            "account_id": os.getenv(account_id_env, ""),
            "access_token": os.getenv(access_token_env, ""),
        }

        super().__init__(config=Config(**config_data))

    def fetch_instruments(self, fetch_all_metadata=False):
        client = oandapyV20.API(access_token=self.config.access_token)
        instruments = accounts.AccountInstruments(accountID=self.config.account_id)
        response = client.request(instruments)

        if fetch_all_metadata:
            return response
        else:
            return [
                instrument["name"] for instrument in response.get("instruments", [])
            ]


if __name__ == "__main__":
    galgoz = Galgoz()
    instruments = galgoz.fetch_instruments()
    print(instruments)
