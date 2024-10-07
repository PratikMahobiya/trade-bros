from time import sleep
from django.db import transaction
from stock.models import Transaction
from django.dispatch import receiver
from django.utils.html import format_html
from django.db.models.signals import post_save
from system_conf.models import Configuration, Symbol
from helper.angel_order import Create_Order, Is_Order_Completed



def colour(value):
    if value == 0:
        return value
    elif value < 0:
        return format_html('<strong style="color:Red;">{}</strong>', value)
    return format_html('<strong style="color:Green;">{}</strong>', value)


def calculate_volatility(dt):
    dt['Return'] = 100 * (dt['Close'].pct_change())
    return dt['Return'].std()


def ExitAction(sender, instance, created):
    try:
        print(f"Pratik: POST EXIT: Check Exit Succeed or Not: {instance.product} : {instance.name} : {instance.symbol} : {instance.type} : {instance.price} :  {instance.order_id}")
        configuration_obj = Configuration.objects.filter(product=instance.product)[0]
        if configuration_obj.place_order and instance.indicate == 'EXIT' and not Is_Order_Completed(instance.order_id):
            symbol_obj = Symbol.objects.get(product=instance.product, symbol=instance.symbol, is_active=True)
            if instance.product == 'future':
                order_id, order_status, price = Create_Order(configuration_obj, 'SELL', 'CARRYFORWARD', symbol_obj.token, instance.symbol, symbol_obj.exchange, instance.price, instance.lot, "MARKET")
            else:
                if instance.mode == 'CE':
                    order_id, order_status, price = Create_Order(configuration_obj, 'SELL', 'DELIVERY', symbol_obj.token, instance.symbol, symbol_obj.exchange, instance.price, instance.lot, "MARKET")
                else:
                    order_id, order_status, price = Create_Order(configuration_obj, 'BUY', 'INTRADAY', symbol_obj.token, instance.symbol, symbol_obj.exchange, instance.price, instance.lot, "MARKET")
            
            if configuration_obj.place_order and (order_id in ['', 0, '0', None]):
                print(f"Pratik: POST EXIT: ERROR: Not Accepting Orders: {instance.symbol} : {order_id}, {order_status}")
                sleep(1)
                ExitAction(sender, instance, created)
            else:
                instance.order_id = order_id
                instance.order_status = order_status
                instance.save()
    except Exception as e:
        print(f"Pratik: POST EXIT: ERROR: {e}")
    return True


@receiver(post_save, sender=Transaction)
def CheckExitSucceedOrNot(sender, instance, created, **kwargs):
  if created:
    sleep(1)
    transaction.on_commit(lambda: ExitAction(sender, instance, created))

