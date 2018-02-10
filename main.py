from livecoin.livecoin_api import LivecoinApi
import main_settings
from telegram_features.telegram_notification import send_notification
from datetime import datetime, timedelta
import random
from telegram.ext.dispatcher import run_async


def init_trader(bot, job):

    trade_bot = LivecoinApi()

    orders_id = trade_bot.get_openorders()

    ex_list = trade_bot.get_partiallyorders()

    shitcoin_list = trade_bot.get_shitcoin_info()

    for dl in shitcoin_list:
        ex_list.append(trade_bot.get_btc_ex(dl))

    # на случай, если не захочется торговать конкретной валютой
    # ex_list.append(trade_bot.get_btc_ex('BCH'))

    cancel_buy_orders_id = []
    for order in orders_id:
        if 'SELL' in orders_id[0]['type']:
            issuetime_order = order['issuetime']
            fuckup_pair = order['pair']
            fuckup_quantity = order['quantity']
            fuckup_price = order['price']
            if datetime.now() - datetime.fromtimestamp(issuetime_order / 1000) >= \
                    timedelta(days=main_settings.default_loss_time):
                trade_bot.cancel_orders(order)
                send_notification('Отменил ордер {order}, {pair}'.format(order=order['id'], pair=order['currencyPair']))
                current_min_ask = trade_bot.get_minask(fuckup_pair)
                trade_bot.sell_currency(fuckup_pair, "{0:.8f}".format(fuckup_quantity),
                                        "{0:.8f}".format(current_min_ask))
                send_notification('Сливаем по текущей цене {current_min_ask} пару {fuckup_pair}, т.к. не смогли '
                                  'продать за {default_loss_time} дней'.format(current_min_ask=current_min_ask,
                                                                       fuckup_pair=fuckup_pair,
                                                                       default_loss_time=main_settings.
                                                                       default_loss_time))
            else:
                current_min_ask = trade_bot.get_minask(trade_bot.get_currency_info(
                    trade_bot.get_coin_details(fuckup_pair)))
                send_notification('Застряли в {pair}. Объём сделки: {quantity}. Курс в ордере {order_price}. '
                                  'Курс текущий {current_min_ask}. Либо ждем 14 дней, либо мониторим эти сообщения '
                                  'и сливаем руками.'
                                  .format(pair=fuckup_pair, quantity=fuckup_quantity, order_price=fuckup_price,
                                          current_min_ask=current_min_ask))
        if 'BUY' in orders_id[0]['type']:
            cancel_buy_orders_id.append(order)
    trade_bot.cancel_orders(cancel_buy_orders_id)

    balances = trade_bot.get_balanses_available()
    send_notification('Доступный для торговли баланс: {}'.format(balances))

    btc_balance = trade_bot.get_btc_balance(balances)

    for balance in balances:
        if str(balance).upper() != 'BTC' and ((trade_bot.get_btc_ex(balance)) not in ex_list):
            ex_list.append(trade_bot.get_btc_ex(balance))
            # продаем эту валюту
            buys_pr = trade_bot.get_buy_price(trade_bot.get_btc_ex(balance))
            if buys_pr == 0:
                send_notification('Этой валютой не торговали: {}'.format(str(balance).upper()))
                continue
            coin_details = trade_bot.get_coin_details(trade_bot.get_btc_ex(balance))
            if not trade_bot.is_Error(coin_details):
                coin_details = trade_bot.get_currency_info(coin_details)
                min_ask = trade_bot.get_minask(coin_details) - main_settings.sell_step
                if buys_pr * (1 + main_settings.min_delta) < min_ask:
                    trade_bot.sell_currency(trade_bot.get_btc_ex(balance), "{0:.8f}".format(balances[balance]),
                                            "{0:.8f}".format(min_ask))
                else:
                    send_notification('Не подходящий курс для продажи {}, попробуем в следующий заход'.format(balance))

    order_size = trade_bot.get_min_order_size(main_settings.min_order_mult)
    max_num_orders = int((btc_balance * 0.99) / order_size)

    pair_ls = trade_bot.get_market_conditions()

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

    # if max_num_orders > 3:
    if max_num_orders > len(rg_list):
        # max_num_orders = 3
        max_num_orders = len(rg_list)

    if max_num_orders > 0:
        order_size = (btc_balance * 0.99) / max_num_orders

        # while (order_size * max_num_orders) > (0.001 * 0.99):
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

    job.interval = random.randint(60, 180)

if __name__ == '__main__':
    init_trader()
