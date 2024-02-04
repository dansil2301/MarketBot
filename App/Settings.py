from tokenData.TokenData import TokenData


class Settings:
    def __init__(self):
        self.TOKEN = TokenData().GetToken("SANDBOX_TOKEN")
        self.figi = "BBG004730N88"
        self.percent_down = -5
