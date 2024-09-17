import requests
from system_conf.models import Symbol
from datetime import datetime

def Symbol_Setup():
    url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
    data = requests.get(url).json()
    
    for i in data:
        product = None
        if i['instrumenttype'] in ['OPTSTK', 'OPTIDX']:
            product = 'option'
        # elif i['instrumenttype'] in ['OPTFUT']:
        #     product = 'future'
        elif i['symbol'].endswith('-EQ'):
            product = 'equity'
        if product is not None:
            obj, _ = Symbol.objects.get_or_create(
                product=product,
                name=i['name'],
                token=i['token'],
                symbol=i['symbol'],
                strike=i['strike']/100,
                exchange=i['exch_seg'],
                expiry=datetime.strptime(i['expiry'], '%d%b%Y'),
                lot=i['lotsize']
            )
    return True
