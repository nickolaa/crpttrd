import hashlib
import hmac
from urllib.parse import urlencode
import requests
# торгуем парой BTC/USD
# maxBid продать BTC получить USD - я создаю орде на продажу
# maxAsk купить BTC потратить USD - я создаю ордер на покупку

# доступ к API-серверу
server = 'https://api.livecoin.net'
api_key = ''
sign_key = ''.encode('utf-8')
trade_pairs = {'currpair': ['XMR/BTC', 'LTC/BTC', 'BCH/BTC'], 'coin': ['XMR', 'LTC', 'BCH']}  # 'BTC/USD',

# получаем данные по интересуемые пары валют
def currpair_info():

    # arraycurr = []
    arraycurr = {'symbol': [], 'volume': [], 'best_bid': [], 'best_ask': []}
    for currency in trade_pairs['currpair']:
        # print(currency)
        res = requests.get(server + '/exchange/ticker' + '?currencyPair=' + currency)
        # max_bid_min_ask = requests.get(server + '/exchange/maxbid_minask' + '?currencyPair=' + currency) # /exchange/maxbid_minask эта инфа есть в ticker
        # print(max_bid_min_ask.json())
        # print(res.json())
        # print(res.json()['symbol'], res.json()['volume'], res.json()['best_bid'], res.json()['best_ask'])
        # arraycurr.append(res.json()['symbol'])
        for key in arraycurr:
            arraycurr[key].append(res.json()[key])
        # arraycurr['symbol'].append(res.json()['symbol'])
        # arraycurr['volume'].append(res.json()['volume'])
        # arraycurr['best_ask'].append(res.json()['best_ask'])
        # arraycurr['best_bid'].append(res.json()['best_bid'])
    return arraycurr
        # return res.json()['symbol'], res.json()['volume'], res.json()['best_bid'], res.json()['best_ask']
# {'symbol': ['BTC/USD', 'XMR/BTC', 'LTC/BTC', 'BCH/BTC'], 'volume': [629.74500802, 6618.04616727, 10615.37148271, 1251.04576929], 'best_bid': [14151, 0.02538255, 0.01704259, 0.17125692], 'best_ask': [14399.99, 0.025989, 0.01734954, 0.17553979]}

    # return arraycurr
    #     # return res.json()['symbol'], res.json()['volume'], res.json()['best_bid'], res.json()['best_ask']


# currpair_info()
# print(currpair_info())

# вытаскиваем текущий баланс пользователя по определенным валютам
def get_my_balance():
    params = {'currency': 'BTC,USD,XMR,LTC,BCH'}
    encoded_params = urlencode(params)
    sign = hmac.new(sign_key, msg=encoded_params.encode('utf-8'), digestmod=hashlib.sha256).hexdigest().upper()
    headers = {"Api-key": api_key, "Sign": sign}
    res = requests.get(server + '/payment/balances', params=params, headers=headers)
    # print(res.url)
    # print(res.json())
    balances = []
    for element in res.json():
        if element['type'] == 'available':
            balances.append(element)
    # print(balances)
    return balances
# [{'type': 'available', 'currency': 'BTC', 'value': 0.0}, {'type': 'available', 'currency': 'USD', 'value': 0.0}, {'type': 'available', 'currency': 'XMR', 'value': 0.0}, {'type': 'available', 'currency': 'LTC', 'value': 0.0}, {'type': 'available', 'currency': 'BCH', 'value': 0.0}]



def get_coin_info():
    get_coin_info = requests.get(server + '/info/coinInfo')
    # print(get_coin_info.json())
    coin_info = get_coin_info.json()
    get_coin_info_list = {'name': [], 'symbol': [], 'walletStatus': [], 'withdrawFee': [], 'difficulty': [], 'minDepositAmount': [], 'minWithdrawAmount': [], 'minOrderAmount': []}
    for currency in coin_info['info']:
        if currency['symbol'] not in ['BTC', 'LTC', 'XMR', 'BCH']:
            continue
        for key, value in currency.items():
            get_coin_info_list[key].append(value)
    # for key in coin_info['info'][0]:
    #     if coin_info['info'][0]['symbol'] in ['BTC', 'LTC', 'XMR', 'BCH']:
    #         get_coin_info_list[key].append(coin_info['info'][0][key])
    return get_coin_info_list
# {'name': ['Bitcoin', 'Litecoin', 'Monero', 'Bitcoin Cash'], 'symbol': ['BTC', 'LTC', 'XMR', 'BCH'], 'walletStatus': ['normal', 'normal', 'normal', 'normal'], 'withdrawFee': [0.001, 0.02, 0.03, 0.001], 'difficulty': [1931136454487.7, 3776554.8541065, None, 255773443583.35], 'minDepositAmount': [0, 0, 0, 0], 'minWithdrawAmount': [' 0.002', '0.01', 0.01, 0.01], 'minOrderAmount': [0.0001, 0.0064, 0.0041, 0.0007]}


def comparison_pair_balance_and_min_order(get_coin_info, get_my_balance, currpair_info):

    for coin in get_coin_info['symbol']:
        if coin == get_my_balance[0]['currency'] and coin != 'BTC' and get_my_balance[0]['currency'] != 'BTC':
            for min_order in get_coin_info['minOrderAmount']:

                    if get_my_balance[0]['value'] < min_order:
                        remove_pair = trade_pairs['coin'][coin].index(coin)
                        trade_pairs['currpair'].remove([remove_pair])
    print(trade_pairs)

# balances = get_my_balance()
# print(currpair_info())
# get_coin_info()
# print(get_coin_info())
# print(get_my_balance())

get_coin_info = get_coin_info()
# {'name': ['Bitcoin', 'Litecoin', 'Monero', 'Bitcoin Cash'], 'symbol': ['BTC', 'LTC', 'XMR', 'BCH'], 'walletStatus': ['normal', 'normal', 'normal', 'normal'], 'withdrawFee': [0.001, 0.02, 0.03, 0.001], 'difficulty': [1931136454487.7, 3776554.8541065, None, 255773443583.35], 'minDepositAmount': [0, 0, 0, 0], 'minWithdrawAmount': [' 0.002', '0.01', 0.01, 0.01], 'minOrderAmount': [0.0001, 0.0064, 0.0041, 0.0007]}
get_my_balance = get_my_balance()
# [{'type': 'available', 'currency': 'BTC', 'value': 0.0}, {'type': 'available', 'currency': 'XMR', 'value': 0.0}, {'type': 'available', 'currency': 'LTC', 'value': 0.0}, {'type': 'available', 'currency': 'BCH', 'value': 0.0}]
currpair_info = currpair_info()
# {'symbol': ['XMR/BTC', 'LTC/BTC', 'BCH/BTC'], 'volume': [6618.04616727, 10615.14854271, 1251.04576929], 'best_bid': [0.02538264, 0.01704272, 0.1712571], 'best_ask': [0.025989, 0.0173495, 0.1755397]}
comparison_pair_balance_and_min_order(get_coin_info, get_my_balance, currpair_info)


