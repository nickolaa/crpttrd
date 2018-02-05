import hashlib
import hmac
import requests
from urllib.parse import urlencode
from collections import OrderedDict
from livecoin.keys import api_key
from livecoin.keys import sign_key
from telegram_features.telegram_notification import send_notification

server_url = 'https://api.livecoin.net'
server = 'api.livecoin.net'


class LivecoinApi():
    def __init__(self):
        self.server = server_url

    def transport_query(self, url):
        req = requests.get(url)
        return req.json()

    def get_request(self, method, data):
        encoded_params = urlencode(data)
        sign = hmac.new(sign_key.encode(), msg=encoded_params.encode('utf-8'), digestmod=hashlib.sha256).hexdigest().upper()
        headers = {"Api-key": api_key, "Sign": sign}
        response = requests.get(server_url + method, params=data, headers=headers)
        return response

    def post_request(self, method, data):
        encoded_data = urlencode(data)
        sign = hmac.new(sign_key.encode(), msg=encoded_data.encode(), digestmod=hashlib.sha256).hexdigest().upper()
        headers = {"Api-key": api_key, "Sign": sign, "Content-type": "application/x-www-form-urlencoded"}
        response = requests.post(server_url + method, data=data, headers=headers)
        return response

    def get_market_conditions(self):
        return self.transport_query(server_url + '/exchange/ticker')

    def get_shitcoin_info(self):
        shitcoinlist = []
        shitcoin = self.transport_query(server_url + '/info/coinInfo')
        for coin in shitcoin['info']:
            if coin['walletStatus'] != 'normal':
                shitcoinlist.append(coin['symbol'])
        return shitcoinlist

    def get_coin_details(self, pair):
        return self.transport_query(server_url + '/exchange/maxbid_minask?currencyPair=' + pair)

    def get_volume(self, coin):
        return float(coin['volume']) * float(coin['last'])

    def is_btc(self, pair):
        return '/BTC' in pair

    def get_pair(self, pair):
        return pair['symbol']

    def get_low(self, pair):
        return pair['low']

    def get_high(self, pair):
        return pair['high']

    def get_best_bid(self, pair):
        return pair['best_bid']

    def get_best_ask(self, pair):
        return pair['best_ask']

    def is_Error(self, req):
        return 'errorCode' in req

    def get_currency_info(self, req):
        return req['currencyPairs'][0]

    def get_minask(self, pair):
        return float(pair['minAsk'])

    def get_maxbid(self, pair):
        return float(pair['maxBid'])

    def get_balanses(self):
        method = '/payment/balances'
        data = OrderedDict([])
        response = self.get_request(method, data)
        coin_list = response.json()
        balances = {}
        for coin in coin_list:
            if ('None' not in str(coin['value'])):
                if (coin['value'] > 0):
                    if coin['currency'] not in balances:
                        balances[coin['currency']] = coin['value']

        return balances

    def get_openorders(self):
        method = '/exchange/client_orders'
        data = OrderedDict(sorted([('openClosed', 'OPEN')]))
        response = self.get_request(method, data)
        openorders = response.json()
        orders_id = []
        if openorders['totalRows'] > 0:
            openorders = openorders['data']
            for order in openorders:
                if order['orderStatus'] == 'OPEN':
                    orders_id.append({'pair': order['currencyPair'], 'id': order['id'], 'issuetime': order['issueTime']})
        return orders_id

    def get_partiallyorders(self):
        method = '/exchange/client_orders'
        data = OrderedDict(sorted([('openClosed', 'PARTIALLY')]))
        response = self.get_request(method, data)
        partiallyorders = response.json()
        order_pairs = []
        if partiallyorders['totalRows'] > 0:
            partiallyorders = partiallyorders['data']
            for order in partiallyorders:
                if order['orderStatus'] == 'PARTIALLY_FILLED':
                    order_pairs.append(order['currencyPair'])
                if order['orderStatus'] == 'PARTIALLY':
                    order_pairs.append(order['currencyPair'])
        return order_pairs

    def get_buy_price(self, pair):
        '''
            Выдать цену покупки имеющеёся валюты
        :param pair:
        :return: float
        '''
        method = '/exchange/trades'
        data = OrderedDict(sorted([('currencyPair', pair)]))
        response = self.get_request(method, data)
        orders = response.json()
        if 'success' in orders:
            if orders['success'] == False:
                return 0
        sum = 0
        for tr_type in orders:
            if tr_type['type'] == 'sell':
                break
            else:
                sum = tr_type['price']
        return sum

    def cancel_orders(self, orders_id):
        method = "/exchange/cancellimit"
        for order in orders_id:
            data = OrderedDict(sorted([('currencyPair', order['pair']), ('orderId', order['id'])]))
            response = self.post_request(method, data)
            value = response.json()
            if value['cancelled'] == True:
                send_notification('успешно отменен ордер # {order} объёмом {value}, {orderpair}'.
                                  format(order=order['id'], value=value['quantity'], orderpair=order['pair']))
            else:
                send_notification('ошибка отмены ордера #{order}, {orderpair}'.
                                  format(order=order['id'], orderpair=order['pair']))

    def buy_currency(self, pair, quantity, price):
        method = "/exchange/buylimit"
        data = OrderedDict(sorted([('currencyPair', pair), ('price', price), ('quantity', quantity)]))
        response = self.post_request(method, data)
        value = response.json()
        if value['success'] == True:
            send_notification('успешно создан ордер на покупку {quantity}, {pair}, по курсу {price} ID: {value}'.
                              format(quantity=str(quantity), pair=pair, price=str(price), value=value['orderId']))
        else:
            send_notification('уже есть ордер на продажу ID: {value}'.format(value=value['orderId']))

    def sell_currency(self, pair, quantity, price):
        method = "/exchange/selllimit"
        data = OrderedDict(sorted([('currencyPair', pair), ('price', price), ('quantity', quantity)]))
        response = self.post_request(method, data)
        value = response.json()
        if value['success'] == True:
            send_notification('успешно создан ордер на продажу{quantity}, {pair}, по курсу {price} : {value}'.
                              format(quantity=str(quantity), pair=pair, price=str(price), value=value['orderId']))
        else:
            send_notification(value)

    def get_btc_ex(self, cur):
        return cur + '/BTC'

    def get_btc_balance(self, balance):
        if 'BTC' in balance:
            return balance['BTC']
        else:
            return 0

    def get_min_order_size(self, mult):
        return 0.0001 * mult
