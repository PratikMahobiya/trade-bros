import datetime
import pandas as pd
import requests


def Get_data_frame_angel_tokens():
    url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
    res = requests.get(url).json()
    token_df = pd.DataFrame.from_dict(res)
    token_df['expiry'] = pd.to_datetime(token_df['expiry'])
    token_df = token_df.astype({'strike': float})
    return token_df


def get_token_option_index_info(df, exch_seg, instrumenttype, symbol, strike_price, pe_ce):
    if exch_seg in ['NFO', 'BFO'] and instrumenttype in ['OPTSTK', 'OPTIDX']:

        date = datetime.date.today()

        strike_price = strike_price * 100
        return df[(df['exch_seg'] == exch_seg) & (df['instrumenttype'] == instrumenttype) & (df['name'] == symbol) & (df['strike'] == strike_price) & (df['symbol'].str.endswith(pe_ce)) & (df['expiry'] > str(date))].sort_values(by=['expiry']).iloc[0]