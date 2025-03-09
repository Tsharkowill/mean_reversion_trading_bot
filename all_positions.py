import bitget.v2.mix.account_api as mixAccountApi
from decouple import config

apiKey = config('apiKey')
secretKey = config('secretKey')
passphrase = config('passphrase')


params = {
            "productType": "USDT-FUTURES",
            "marginCoin": "USDT"
        }



account_api = mixAccountApi.AccountApi(apiKey, secretKey, passphrase)

response_base = account_api.allPosition(params)