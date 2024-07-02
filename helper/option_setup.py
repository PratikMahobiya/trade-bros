import numpy as np
from datetime import datetime
from time import sleep
from logs.logger import write_error_log, write_info_log
from helper.angel_token import Get_data_frame_angel_tokens, get_token_option_index_info
from option.models import Index, OptionSymbol
from zoneinfo import ZoneInfo

 
def closest_value(input_list, input_value, gap):
  arr = np.asarray(input_list)
  i = (np.abs(arr - input_value)).argmin()
  return sorted(list(range(arr[i], arr[i]-5000, -gap)[:20]) + list(range(arr[i], arr[i]+5000, gap)[1:20]))


def get_month_val(month):
    if month == 'Jan': return 1
    elif month == 'Feb': return 2
    elif month == 'Mar': return 3
    elif month == 'Apr': return 4
    elif month == 'May': return 5
    elif month == 'Jun': return 6
    elif month == 'Jul': return 7
    elif month == 'Aug': return 8
    elif month == 'Sep': return 9
    elif month == 'Oct': return 'O'
    elif month == 'Nov': return 'N'
    elif month == 'Dec': return 'D'
    else: return month


def get_month_name(month):
    if month == 'Jan': return 'JAN'
    elif month == 'Feb': return 'FEB'
    elif month == 'Mar': return 'MAR'
    elif month == 'Apr': return 'APR'
    elif month == 'May': return 'MAY'
    elif month == 'Jun': return 'JUN'
    elif month == 'Jul': return 'JUL'
    elif month == 'Aug': return 'AUG'
    elif month == 'Sep': return 'SEP'
    elif month == 'Oct': return 'OCT'
    elif month == 'Nov': return 'NOV'
    elif month == 'Dec': return 'DEC'
    else: return month


def StockConfigs(data, logger):
    write_info_log(logger, 'StockConfig: Started')

    # Create Index in Index Table
    for index, data_list in data.items():
        try:
            # STORE IN STOCK TABLE
            index_obj_list = Index.objects.filter(index=index)
            if not index_obj_list:
                Index.objects.create(index=index, index_symbol=data_list[0], expiry_date=datetime.strptime(data_list[1], '%d-%b-%Y'), chain_strike_price_diff=data_list[2]*0.8)
            else:
                index_obj_list.update(expiry_date=datetime.strptime(data_list[1], '%d-%b-%Y'), chain_strike_price_diff=data_list[2]*0.8, is_active=True)
        except Exception as e:
            write_error_log(logger, f'{e} {index}')
        write_info_log(logger, f"Index Creation Completed")

    write_info_log(logger, 'StockConfig: Ended')
    return True


def GetVelocity(data, conn, logger):
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))

    write_info_log(logger, 'GetVelocity: Started')

    angel_token_df = Get_data_frame_angel_tokens()
    for index, data_list in data.items():
        sleep(0.2)
        option_chain_data = list(range(0, 500000, data_list[2]))
        strike_price_list = closest_value(option_chain_data, conn.quotes({"symbols": data_list[0]})['d'][0]['v']['lp'], data_list[2])
        for strikeprice in strike_price_list:
            try:
                symbol_key = f"{data_list[0][:4]}{index}{now.strftime('%y')}{get_month_val(data_list[1][3:6])}{data_list[1][:2]}{strikeprice}"
                if int(data_list[1][:2]) in [25, 26, 27, 28, 29, 30, 31]:#23, 24, 
                    symbol_key = f"{data_list[0][:4]}{index}{now.strftime('%y')}{get_month_name(data_list[1][3:6])}{strikeprice}"
                if data_list[0][:3] == 'BSE':
                    exch_seg = 'BFO'
                else:
                    exch_seg = 'NFO'
                call_token_info = get_token_option_index_info(angel_token_df, exch_seg, 'OPTIDX', index, strikeprice,'CE')
                put_token_info = get_token_option_index_info(angel_token_df, exch_seg, 'OPTIDX', index, strikeprice,'PE')

                if not OptionSymbol.objects.filter(strike_price=strikeprice, symbol=f"{symbol_key}", is_active=True).exists():
                    OptionSymbol.objects.create(
                        index=Index.objects.get(index=index),
                        strike_price=strikeprice,
                        symbol=f"{symbol_key}",
                        call_token=call_token_info['token'],
                        call_angel_symbol=call_token_info['symbol'],
                        lot=call_token_info['lotsize'],
                        put_token=put_token_info['token'],
                        put_angel_symbol=put_token_info['symbol'])
            except Exception as e:
                write_error_log(logger, f'{e}')
                write_error_log(logger, f'{symbol_key}')

    write_info_log(logger, 'GetVelocity: Ended')
    return True