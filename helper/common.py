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