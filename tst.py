def currpair_info():
    pairs = {'currpair': ['BTC/USD', 'XMR/BTC', 'LTC/BTC', 'BCH/BTC']}
    # в key_name список параметров API которые выдает сервер
    # если внезапно сервер изменит названия параметров, то нужно поменять в key_name
    key_name = ['symbol', 'volume', 'best_ask', 'best_bid']
    # arraycurr пустой словарь списков, чтобы разложить по нужным ключам-параметрам
    arraycurr = {key_name[0]: [], key_name[1]: [], key_name[2]: [], key_name[3]: []}
    for currency in pairs['currpair']:
        res = requests.get(server + '/exchange/ticker' + '?currencyPair=' + currency)
        # print(res.json()['symbol'], res.json()['volume'], res.json()['best_bid'], res.json()['best_ask'])
        arraycurr[key_name].append(res.json()[key_name])

    return arraycurr

print(currpair_info())

# else:
#     arraycurr[key_name] = value_name

# arraycurr['symbol'].append(res.json()['symbol'])
# arraycurr['volume'].append(res.json()['volume'])
# arraycurr['best_ask'].append(res.json()['best_ask'])
# arraycurr['best_bid'].append(res.json()['best_bid'])