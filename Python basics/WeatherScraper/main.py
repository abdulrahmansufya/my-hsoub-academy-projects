# importing libraries

from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import date
from tabulate import tabulate
import json


def get_forecast_data():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--log-level=3')

    prefs = {
        "profile.default_content_setting_values": {
            "images": 2,
            "plugins": 2,
            "popups": 2,
            "notifications": 2,
            "media_stream": 2,
        }
    }
    options.add_experimental_option("prefs", prefs)

    try:
        driver = webdriver.Chrome(options=options)
        driver.get("https://world-weather.info/")

        # انتظار لمدة تصل إلى 10 ثوانٍ حتى يظهر عنصر resorts
        print("loading Data...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "resorts"))
        )

        driver.add_cookie({'name': 'celsius', 'value': '1', 'domain': 'world-weather.info'})
        driver.refresh()

        # انتظار مرة أخرى بعد التحديث
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "resorts"))
        )

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        resorts = soup.find("div", id="resorts")

        if not resorts:
            print("Data not found")
            driver.quit()
            return

        re_cities = r'">([\w\s]+)<\/a><span>'
        cities = re.findall(re_cities, str(resorts))

        re_temps = r'<span>(\+\d+|-\d+)<span'
        temps = re.findall(re_temps, str(resorts))
        temps = [int(temp) for temp in temps]

        conditions_tags = resorts.find_all('span', class_='tooltip')
        conditions = [condition.get(
            'title') for condition in conditions_tags if condition.get('title')]

        if conditions:
            data = zip(cities, temps, conditions)

            return data
        else:
            print("Weather conditions not found")

        driver.quit()

    except Exception as e:
        print(f"An error occurred: {e}")
        driver.quit()


def get_forecast_txt():
    data = get_forecast_data()

    if data:
        today = date.today().strftime("%d %m, %Y")
        with open('output.txt', 'w',encoding='utf-8') as f:
            f.write('popular cities forecast' + '\n')
            f.write(today + '\n')
            f.write('=' * 23 + '\n')
            table = tabulate(data, headers=['city', 'temp', 'condition'], tablefmt='psql')
            f.write(table)


def get_forecast_json():
    data = get_forecast_data()
    if data:
        today = date.today().strftime("%d %m, %Y")
        cities = [{'city': city, 'temp': temp, 'condition': condition} for city, temp, condition in data]
        data_json = {'title': 'popular cities forecast', 'data': today, 'cities': cities}
        with open('output.json', 'w',encoding='utf-8') as f:
            json.dump(data_json, f, ensure_ascii=False)


if __name__ == '__main__':
    get_forecast_txt()
    get_forecast_json()