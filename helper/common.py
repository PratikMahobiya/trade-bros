from django.utils.html import format_html

def colour(value):
    if value == 0:
        return value
    elif value < 0:
        return format_html('<strong style="color:Red;">{}</strong>', value)
    return format_html('<strong style="color:Green;">{}</strong>', value)


def calculate_volatility(dt):
    dt['Return'] = 100 * (dt['Close'].pct_change())
    daily_volatility = dt['Return'].std()
    return daily_volatility


def up_model(obj, price):
    diff = price - obj.price
    profit = round(((diff/obj.price) * 100), 2)
    if obj.mode == 'CE':
      if profit < 0:
        return format_html('<strong style="color:Red;">{}</strong>', profit)
      return format_html('<strong style="color:Green;">{}</strong>', profit)
    else:
      if profit > 0:
        return format_html('<strong style="color:Red;">{}</strong>', -profit)
      return format_html('<strong style="color:Green;">{}</strong>', -profit)