import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import datetime

import urllib.request
from urllib.parse import urlencode, quote_plus
import json

import api_key

POPULATION = 51829023   # 2020. Dec
DATE_INTERVAL = 7

today = datetime.date.today()
api_first_day = datetime.date.fromisoformat("2021-03-11")
diff = (today - api_first_day).days + 1

base_url = "https://api.odcloud.kr/api"
api_url = base_url + "/15077756/v1/vaccine-stat"

loc_query = '&cond%5Bsido%3A%3AEQ%5D=%EC%A0%84%EA%B5%AD'    # whole country

api_query_params = '?' + urlencode({
    quote_plus('serviceKey'): api_key.api_key,
    quote_plus('perPage'): diff
})

request = urllib.request.Request(api_url + api_query_params + loc_query)
print("API REQUEST")

request.get_method = lambda: 'GET'
api_request_body = urllib.request.urlopen(request).read()
print("API RESPONSE RECEIVED")

print(api_request_body)

api_result = json.loads(api_request_body)

date_array = []
first_cumulative = []
second_cumulative = []

for i, data in enumerate(api_result['data']):
    print(
        data['baseDate'][:11],
        data['accumulatedFirstCnt'],
        data['firstCnt'],
        data['accumulatedSecondCnt'],
        data['secondCnt']
    )
    date_array.append(data['baseDate'][:11]) if i % DATE_INTERVAL == 0 else None

    first_cumulative.append(data['accumulatedFirstCnt'] + data['firstCnt'])
    second_cumulative.append(data['accumulatedSecondCnt'] + data['secondCnt'])

if not api_result['data'][-1]['baseDate'][:11] in date_array:
    date_array.append(api_result['data'][-1]['baseDate'][:11])

xtick_array = [i for i in range(diff) if i % DATE_INTERVAL == 0]
xtick_array.append(diff - 1) if (diff - 1) % DATE_INTERVAL != 0 else None

plt.figure(figsize=(13, 7))
plt.plot(first_cumulative, label='First', marker='.')
plt.plot(second_cumulative, label='Second', marker='.')

plt.annotate("{0:0.1f}%".format(first_cumulative[-1] / POPULATION * 100), (diff - 1, first_cumulative[-1]))
plt.annotate("{0:0.1f}%".format(second_cumulative[-1] / POPULATION * 100), (diff - 1, second_cumulative[-1]))

plt.gca().yaxis.set_major_formatter(PercentFormatter(POPULATION))

plt.xlim(-1, diff)
plt.legend()
plt.grid(alpha=0.5)
plt.xticks(xtick_array, labels=date_array, rotation=45)
plt.tight_layout()

plt.show()
