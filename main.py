# 1. Get all of my robinhood trading data
import robin_stocks as rs
from dotenv import load_dotenv
import os
import pyotp
from helpers import serialize_it
from datetime import datetime
import json

load_dotenv()

USERNAME = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")

totp  = pyotp.TOTP(os.getenv("2FA")).now()
login = rs.authentication.login(USERNAME, PASSWORD, mfa_code=totp)

SYMBOL = input('Enter stock ticker ')

orders = rs.find_stock_orders(symbol=SYMBOL)
current_price = rs.get_stock_quote_by_symbol(symbol=SYMBOL)['last_extended_hours_trade_price']
serialized_orders = serialize_it(orders)
trades = []

for order in serialized_orders:
    max_date = datetime(2020, 6, 1) # the max date we will allow to be included in our trades list.
    last_transaction = datetime.fromisoformat(order['last_transaction_at'][0:-1])
    if ((order['state'] != 'filled' and order['executed_notional'] == None) or last_transaction > max_date):
        continue
    trade = {}
    trade['side'] = order['side']
    trade['last_transaction_at'] = order['last_transaction_at']
    for ex in order['executions']:
        trade['price'] = ex['price']
        trade['quantity'] = ex['quantity']   
    trades.append(trade)


net = 0
maximum_owned_at_once = 0
price_at_max_held_time = 0
current_owned = 0
for trade in reversed(trades):
    if (trade['side'] == 'buy'):
        current_owned += float(trade['quantity'])
        net -= float(trade['price']) * float(trade['quantity'])
    elif (trade['side'] == 'sell'):
        current_owned -= float(trade['quantity'])
        net += float(trade['price']) * float(trade['quantity'])
    if (current_owned > maximum_owned_at_once):
        maximum_owned_at_once = current_owned
        price_at_max_held_time = trade['price']
    print(trade['side'], trade['quantity'], trade['price'], trade['last_transaction_at'])
held_value = float(current_price) * float(maximum_owned_at_once)


print('Price of ', SYMBOL, 'at time of purchase', round(float(price_at_max_held_time), 2))
print('Price of', SYMBOL, 'is currently', round(float(current_price), 2), 'of', SYMBOL)
print('I profitted a total of $', round(net, 2), 'trying to trade ', SYMBOL)
print('The most shares of', SYMBOL, 'I owned at a time was', maximum_owned_at_once)
print('If I had held all of those shares, today it\'d be worth $', round(held_value, 2))
print('My net profit if I had held would\'ve been $', round(held_value - float(price_at_max_held_time) * maximum_owned_at_once, 2))

