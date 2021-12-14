import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter, StrMethodFormatter
import datetime
from datetime import date

import urllib.request
from urllib.parse import urlencode, quote_plus
import json

import api_key

POPULATION = 51349116   # 2020. Dec
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
raw_data = {}

for i, data in enumerate(api_result['data']):
    print(
        data['baseDate'][:11],
        data['totalFirstCnt'],
        data['totalSecondCnt'],
        data['totalThirdCnt'],
        # data['accumulatedFirstCnt'],
        data['firstCnt'],
        # data['accumulatedSecondCnt'],
        data['secondCnt'],
        data['thirdCnt']
    )
    date_array.append(data['baseDate'][:10]) if i % DATE_INTERVAL == 0 else None

    raw_data[data['baseDate'][:10]] = (
        data['totalFirstCnt'],
        data['totalSecondCnt'],
        data['totalThirdCnt'],
        data['firstCnt'],
        data['secondCnt'],
        data['thirdCnt']
    )

raw_data_sorted = sorted(raw_data.items())
_, data = zip(*raw_data_sorted)
first_cumulative, second_cumulative, third_cumulative, first_daily, second_daily, third_daily = zip(*data)

if not api_result['data'][-1]['baseDate'][:10] in date_array:
    date_array.append(api_result['data'][-1]['baseDate'][:10])

xtick_array = [i for i in range(diff) if i % DATE_INTERVAL == 0]
xtick_array.append(diff - 1) if (diff - 1) % DATE_INTERVAL != 0 else None

# To improve xtick visibility
if (date.fromisoformat(date_array[-1]) - date.fromisoformat((date_array[-2]))).days <= 2:
    date_array.pop(-2)
    xtick_array.pop(-2)

# Before 09:35, data is not received yet
if api_result['currentCount'] != diff:
    xtick_array.pop()
    if xtick_array[-1] != diff - 2:
        xtick_array.append(diff - 2)

plt.figure(figsize=(20, 10))

plt.subplot(2, 1, 1)
plt.plot(first_cumulative, label='First', marker='.')
plt.plot(second_cumulative, label='Second', marker='.')
plt.plot(third_cumulative, label='Second', marker='.')

plt.xlabel('1st : {0:,}, 2nd : {1:,}, 3nd : {2:,}\ntotal : {3:,}'.
           format(first_cumulative[-1], second_cumulative[-1], third_cumulative[-1], POPULATION))

plt.title("Accumulated vaccination")

plt.annotate("{0:0.1f}%".format(first_cumulative[-1] / POPULATION * 100), (diff - 1, first_cumulative[-1]))
plt.annotate("{0:0.1f}%".format(second_cumulative[-1] / POPULATION * 100), (diff - 1, second_cumulative[-1]))
plt.annotate("{0:0.1f}%".format(third_cumulative[-1] / POPULATION * 100), (diff - 1, third_cumulative[-1]))

plt.gca().yaxis.set_major_formatter(PercentFormatter(POPULATION))

plt.xlim(-1, diff)
plt.legend()
plt.grid(alpha=0.5)
plt.xticks(xtick_array, labels=date_array, rotation=45)
plt.tight_layout()

plt.subplot(2, 1, 2)

WIDTH = 0.25

plt.bar(np.arange(len(first_daily)) - WIDTH, first_daily, width=WIDTH, label='First')
plt.bar(np.arange(len(second_daily)), second_daily, width=WIDTH, label='Second')
plt.bar(np.arange(len(third_daily)) + WIDTH, third_daily, width=WIDTH, label='Third')

plt.gca().yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))

plt.title("Daily vaccination")

plt.xlim(-1, diff)
plt.legend()
plt.grid(alpha=0.5)
plt.xticks(xtick_array, labels=date_array, rotation=45)
plt.tight_layout()

plt.show()
