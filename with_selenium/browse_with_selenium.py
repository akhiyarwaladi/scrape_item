from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import requests
from slugify import slugify
import time
from selenium.webdriver.firefox.options import Options
import pandas as pd

def init():
    """Scrape-id using Firefox webdriver as a default, 
    here is the list of all supported webdriver
    
    https://www.selenium.dev/documentation/en/getting_started_with_webdriver/browsers/
    https://www.selenium.dev/documentation/en/getting_started_with_webdriver/third_party_drivers_and_plugins/
    
    driver = webdriver.Firefox() 
    """
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    
    return driver
    
def url_harvest_by_keyword(driver, web_url, search_endpoint, keyword, iteration = 1):
    """This method dump json data from shopee endpoint
    based on keyword specified by user
    """
    url= []
    item_api = []
    for iteration in range(iteration):
        headers = {
            'authority': 'shopee.co.id',
            'x-shopee-language': 'id',
            'x-requested-with': 'XMLHttpRequest',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.61',
            'x-api-source': 'pc',
            'accept': '*/*',
        }

        params = (
            ('keyword', keyword),
            ('newest', 50*iteration),
            ('by', 'relevancy'),
            ('limit', 10),
            ('order', 'desc'),
            ('page_type', 'search'),
            ('version', 2),
	    ('official_mall', 1)
        )
        #import urllib.parse
        #keyword_parse = urllib.parse.quote(keyword)
        #parent_url = "https://shopee.co.id/mall/search?keyword={}&order=asc&originalResultType=4&page=0&sortBy=price"\
        #                .format(keyword_parse)
        #print(parent_url)
        #driver.get(parent_url)
        #time.sleep(10)
        #res_item = driver.find_elements_by_xpath('//*[@id="main"]/div/div[2]/div[2]/div[2]/div/div[2]/div[1]')
        #for res in res_item:
        #    print(res.get_attribute("href"))

        try:
            json = requests.get(web_url+search_endpoint, headers=headers, params=params).json()
         
        except ValueError:
            print("Empty response from", web_url)
            driver.quit()
            exit()

        for item in json['items']:
            item_api.append([web_url, item['name'],item['itemid'],item['shopid'],item['price']])

        if len(item_api) <= 0:
            print(item['name'])
            print("NOT FOUND")
            return url


        dfrm = pd.DataFrame(item_api, columns=['url','name','itemid','shopid','price'])
        dfrm['price'] = pd.to_numeric(dfrm['price'])

        print(dfrm)
        dfrm = dfrm.iloc[dfrm['price'].idxmin()]
        
        url.append(search_item_builder(dfrm['url'], dfrm['name'], dfrm['itemid'], dfrm['shopid']))
    return url

def search_item_builder(web_url, item_name, item_id, shop_id):
    """This method build a compact url that
    will be use when scraping
    """
    return web_url+slugify(item_name).lower()+"-i."+str(shop_id)+"."+str(item_id)

def search(driver, url):
    driver.get(url)
    time.sleep(7)

    # Fixed 
    try:
        title = driver.find_elements_by_xpath('//*[@id="main"]/div/div[2]/div[2]/div[2]/div[2]/div[3]/div/div[1]/span')
        price = driver.find_element_by_xpath('//*[@id="main"]/div/div[2]/div[2]/div[2]/div[2]/div[3]/div/div[3]/div/div')
        deskripsi = driver.find_element_by_xpath('//*[@id="main"]/div/div[2]/div[2]/div[2]/div[3]/div[2]/div[1]/div[1]/div[2]/div[2]/div/span')
        category = driver.find_element_by_xpath('//*[@id="main"]/div/div[2]/div[2]/div[2]/div[3]/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/div/a[2]')
        subcategory = driver.find_element_by_xpath('//*[@id="main"]/div/div[2]/div[2]/div[2]/div[3]/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/div/a[3]')
        seller = driver.find_element_by_xpath('//*[@id="main"]/div/div[2]/div[2]/div[2]/div[3]/div[1]/div[1]/div/div[1]')

    except NoSuchElementException: 
        return None 

    product = {
        'url' : url,
        'title' : title[0].text,
        'price' : price.text,
        'desc' : deskripsi.text,
        'category' : category.text,
        'subcategory' : subcategory.text,
        'seller' : seller.text
    }
    # Buggy, still have a bug
    try:
        terjual = driver.find_element_by_xpath('//*[@id="main"]/div/div[2]/div[2]/div[2]/div[2]/div[3]/div/div[2]/div[3]/div[1]')
    except NoSuchElementException:
        terjual = '-'
        product['sold'] = terjual

    try:
        star = driver.find_element_by_xpath('//*[@id="main"]/div/div[2]/div[2]/div[2]/div[2]/div[3]/div/div[2]/div[1]/div[1]')
    except NoSuchElementException:
        star = '-'
        product['star'] = star

    try:
        subsubcategory = driver.find_element_by_xpath('//*[@id="main"]/div/div[2]/div[2]/div[2]/div[3]/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/div/a[4]')
    except NoSuchElementException:
        subsubcategory = '-'
        product['subsubcategory'] = subsubcategory
    
    try:
        city = driver.find_element_by_xpath('//*[@id="main"]/div/div[2]/div[2]/div[2]/div[3]/div[2]/div[1]/div[1]/div[1]/div[2]/div[6]/div')
    except NoSuchElementException:
        city = '-'
        product['city'] = city

    if(subsubcategory != '-'):
        product['subsubcategory'] = subsubcategory.text
    if(city != '-'):
        product['city'] = city.text
    if(terjual != '-'):
        product['sold'] = terjual.text
    if(star != '-'):
        product['star'] = star.text

    return product
