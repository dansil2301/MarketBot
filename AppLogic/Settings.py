from tokenData.TokenData import TokenData


class Settings:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        self.TOKEN = TokenData().GetToken("SANDBOX_TOKEN")
        self.figi = "BBG004730N88"
        self.broker_commission = 0.05
        self.percent_down = 0.75
        self.percent_up = 1.5
