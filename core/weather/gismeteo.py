import re
from datetime import datetime, time, timedelta
import json

import dateparser
import requests
from bs4 import BeautifulSoup

from core.sites.utils import stop_proxy, update_proxy, DEFAULTS_TIMEOUT

url = "https://www.gismeteo.ru/weather-sankt-peterburg-4079/hourly/"

payload = {}
headers = {
    'authority': 'www.gismeteo.ru',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    'dnt': '1',
    'referer': 'https://www.google.com/',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
    'Cookie': 'ab_audience_3=81'
}


def parsing_gismeteo():
    from core.models import ParsingPrecipitation

    response = requests.request("GET", url, headers=headers, data=payload)
    now = datetime.now()
    current_date = datetime.now().date()

    soup_all = BeautifulSoup(response.text)
    rain = soup_all.find("div", {"class": "widget-row widget-row-precipitation-bars row-with-caption"}).find_all("div",
                                                                                                                 {
                                                                                                                     "class": "row-item"})[
           :3]
    date = soup_all.find("div", {"class": "widget-row widget-row-datetime-time"}).find_all("div",
                                                                                           {"class": "row-item"})[
           :len(rain)]
    result = []
    ids = {}

    for i, d in enumerate(date):
        specified_time = time(*[int(t) for t in d.text.split(":")])
        date_time_with_specified_time = datetime.combine(current_date, specified_time)
        if now > date_time_with_specified_time:
            date_time_with_specified_time += timedelta(days=1)
        level = float(rain[i].text.replace(",", "."))
        result.append(ParsingPrecipitation(created_date=date_time_with_specified_time,
                                           level=level))
        ids[date_time_with_specified_time] = level
    ParsingPrecipitation.objects.bulk_create(
        result, batch_size=200, ignore_conflicts=True
    )
    # save_results = ParsingPrecipitation.objects.filter(created_date__in=list(ids.keys()))
    #
    # updates = []
    # for r in save_results:
    #     if ids.get(r.created_date) and abs(r.level - ids.get(r.created_date)) >= 0.1:
    #         r.level = ids.get(r.created_date)
    #         r.save(update_fields=["level"])
    #

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    articles, proxy = parsing_gismeteo()
    print(1)
