import json
import os


class TokenData:
    def __init__(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.TokenFilePath = os.path.join(script_dir, "Client_config.json")

    def GetToken(self, type: str) -> str:
        try:
            with open(self.TokenFilePath, "r") as tokenFile:
                token = json.load(tokenFile)
                if type == "TOKEN":
                    return token["TOKEN"]
                elif type == "SANDBOX_TOKEN":
                    return token["SANDBOX_TOKEN"]
                else:
                    raise Exception("Parameter error")
        except:
            return "Error: can't read token"
