from livecoin.livecoin_api import LivecoinApi
import main_settings
from telegram_features.telegram_notification import send_notification

trade_bot = LivecoinApi()

orders_id = trade_bot.get_openorders()

ex_list = trade_bot.get_partiallyorders()

shitcoin_list = trade_bot.get_shitcoin_info()

for dl in shitcoin_list:
    ex_list.append(trade_bot.get_btc_ex(dl))

# на случай, если не захочется торговать конкретной валютой
# ex_list.append(trade_bot.get_btc_ex('BCH'))

trade_bot.cancel_orders(orders_id)

balances = trade_bot.get_balanses()
# print(balances)

btc_balance = trade_bot.get_btc_balance(balances)

for balance in balances:
    if str(balance).upper() != 'BTC' and ((trade_bot.get_btc_ex(balance)) not in ex_list):
        ex_list.append(trade_bot.get_btc_ex(balance))
        # продаем эту валюту
        buys_pr = trade_bot.get_buy_price(trade_bot.get_btc_ex(balance))
        if buys_pr == 0:
            # bot.send_message(251077347, 'Этой валютой не торговали: ' + str(balance).upper())
            send_notification('Этой валютой не торговали: ' + str(balance).upper())
            # print('Этой валютой не торговали: ' + str(balance).upper())
            # greet_user('Этой валютой не торговали: ' + str(balance).upper())
            continue
        coin_details = trade_bot.get_coin_details(trade_bot.get_btc_ex(balance))
        if not trade_bot.is_Error(coin_details):
            coin_details = trade_bot.get_currency_info(coin_details)
            min_ask = trade_bot.get_minask(coin_details) - main_settings.sell_step
            if buys_pr * (1 + main_settings.min_delta) < min_ask:
                trade_bot.sell_currency(trade_bot.get_btc_ex(balance), "{0:.8f}".format(balances[balance]),
                                        "{0:.8f}".format(min_ask))
            else:
                # print('Wait in ' + balance)
                send_notification('Ждем момента для слива: ' + balance)
                # greet_user('Wait in ' + balance)

order_size = trade_bot.get_min_order_size(main_settings.min_order_mult)
max_num_orders = int((btc_balance * 0.99) / order_size)

pair_ls = trade_bot.get_market_conditions()
# eth_data = list(filter(lambda x: x.get('symbol') == 'LTC/BTC', pair_ls))
# if eth_data:
#     pair_ls = eth_data

rg_list = []

# анализ торговых пар
for coin_pair in pair_ls:
    vol = trade_bot.get_volume(coin_pair)
    symbol = trade_bot.get_pair(coin_pair)
    low = trade_bot.get_low(coin_pair)
    high = trade_bot.get_high(coin_pair)
    best_bid = trade_bot.get_best_bid(coin_pair)
    best_ask = trade_bot.get_best_ask(coin_pair)
    if high > low:
        dev = (high - low) / low
    else:
        dev = main_settings.max_dev
    if (vol > main_settings.min_volume) and (low > main_settings.min_ask) and trade_bot.is_btc(symbol) \
            and (symbol not in ex_list) and (dev < main_settings.max_dev):
        pr = (best_ask - best_bid - main_settings.buy_step - main_settings.sell_step) / \
             (best_bid + main_settings.buy_step)
        rang = pr * vol
        if (pr > main_settings.min_profit) and (pr <= main_settings.max_profit):
            rg_list.append({'rang': rang, 'symbol': symbol})

rg_list.sort(key=lambda i: i['rang'], reverse=True)

if max_num_orders > len(rg_list):
    max_num_orders = len(rg_list)

if max_num_orders > 0:
    order_size = (btc_balance * 0.99) / max_num_orders

    while (order_size * max_num_orders) > (btc_balance * 0.99):
        order_size -= 0.00000001

i = 0
for k in rg_list:
    if i < max_num_orders:
        coin_details = trade_bot.get_coin_details(k['symbol'])
        if not trade_bot.is_Error(coin_details):
            coin_details = trade_bot.get_currency_info(coin_details)
            max_bid = trade_bot.get_maxbid(coin_details) + main_settings.buy_step
            quantity = order_size / max_bid
            trade_bot.buy_currency(k['symbol'], "{0:.8f}".format(quantity), "{0:.8f}".format(max_bid))
    else:
        break
    btc_balance -= order_size
    if btc_balance < order_size:
        order_size = btc_balance
    i += 1
