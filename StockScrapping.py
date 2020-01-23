from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import requests
import json


class PriceProfit:
    def __init__(self):
        chromeOptions = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2}
        chromeOptions.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(
            options=chromeOptions, executable_path=r"C:\\Users\\beroz\\Pictures\\chromedriver.exe")

    def navigate_link(self, link):
        self.driver.get(link)

    def find_price_profit(self):
        driver = self.driver
        self.navigate_link(
            'https://www.isyatirim.com.tr/tr-tr/analiz/hisse/Sayfalar/Temel-Degerler-Ve-Oranlar.aspx#page-5')
        table = driver.find_element_by_id('temelTBody_Finansal')
        rows = table.find_elements_by_tag_name('tr')
        for row in rows:
            stock = row.find_element_by_class_name('sorting_1').text
            try:
                price_profit = float(row.find_elements_by_class_name(
                    'text-right')[1].text.replace(',', '.'))
            except ValueError:
                price_profit = float(0)
            try:
                pd_dd = float(row.find_elements_by_class_name(
                    'text-right')[4].text.replace(',', '.'))
            except ValueError:
                pd_dd = float(0)

            requests.post("http://34.67.211.44/api/ticker/add-fk",
                          {"name": f'{stock}.IS', "fk": price_profit, "pd_dd": pd_dd})

            print(stock)


price_profit = PriceProfit()
price_profit.find_price_profit()
