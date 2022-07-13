from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options

import random
import requests
import time
import os

from slugify import slugify

import pandas as pd
import numpy as np
import re


from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By



from sqlalchemy import event,create_engine,types
driver = 'oracle'
server = '10.234.152.61' 
database = 'alfabi' 
username = 'report' 
password = 'justd0it'
engine_stmt = "%s://%s:%s@%s/%s" % ( driver, username, password, server, database )


def res_to_db(tup_res):

    engine = create_engine(engine_stmt)
    con = engine.connect()

    q_del = """

        DELETE FROM ALFAGIFT_COMPETITIVENESS
        WHERE AC_PLU = '{}' and AC_COMPETITOR = '{}'
    """.format(tup_res[0], tup_res[5])

    con.execute(q_del)

    q_insert = """
        INSERT INTO ALFAGIFT_COMPETITIVENESS 
        (AC_PLU, AC_SOURCE, AC_PRODUCT_NAME, AC_PRICE_NORMAL, AC_PRICE_FINAL, AC_COMPETITOR) 
        VALUES (:AC_PLU, :AC_SOURCE, :AC_PRODUCT_NAME, :AC_PRICE_NORMAL, :AC_PRICE_FINAL, :AC_COMPETITOR)

    """
    con.execute(q_insert, tup_res)

    con.close()


    return 0

def rupiah_format_to_number2(rupiah_format):

    # price normal dan price final biasanya dipisahkan oleh newline
    split_price = rupiah_format.split('\n')

    if split_price is np.nan:
        return np.nan

    # jika element yang telah di split terbagi 2
    if len(split_price) >= 2:
        price_normal = split_price[0]
        price_normal = re.findall('Rp ([^\s]+)', price_normal)
        price_normal = 'Rp' + price_normal[0]

        price_final = split_price[1]
        price_final = re.findall('Rp ([^\s]+)', price_final)
        price_final = 'Rp' + price_final[0]

    # jika element yang telah di split hanya 1
    elif len(split_price) == 1:
        price_final = split_price[0]

        # if ternyata hasilnya panjang sekali kita harus ulang mencari Rp di text
        if len(price_final) > 20:
            price_final = re.findall('Rp ([^\s]+)', price_final)
            price_final = 'Rp' + price_final[0]

        price_normal = price_final
    else:
        price = split_price[0]

    return price_normal, price_final




def rupiah_format_to_number1(rupiah_format):

    rupiah_number = int(rupiah_format.split('Rp')[-1].replace(".",""))

    return rupiah_number





def init():
    """Scrape-id using Firefox webdriver as a default, 
    here is the list of all supported webdriver
    
    https://www.selenium.dev/documentation/en/getting_started_with_webdriver/browsers/
    https://www.selenium.dev/documentation/en/getting_started_with_webdriver/third_party_drivers_and_plugins/
    
    driver = webdriver.Firefox() 
    """
    # options = Options()
    # options.headless = False
    # driver = webdriver.Firefox(executable_path='/home/server/script/geckodriver', options=options)


    options = webdriver.ChromeOptions()
    # Path to your chrome profile or you can open chrome and type: "chrome://version/" on URL
    options.add_argument('--headless')
    options.add_argument('--user-data-dir=/home/server/.config/google-chrome/')
    options.add_argument('--profile-directory=Profile 3') 
    options.add_argument('--start-maximized')
    options.add_argument('--disable-dev-shm-usage')

    chrome_driver_exe_path = os.path.abspath('/home/server/gli-data-science/akhiyar/scrape_product/chromedriver') 
    driver = webdriver.Chrome(executable_path=chrome_driver_exe_path, options=options)

    
    return driver
    


def url_harvest_by_keyword(driver, web_url, search_endpoint, keyword, iteration = 1):
    """This method dump json data from shopee endpoint
    based on keyword specified by user
    """
    url= []
    item_api = []
    # for iteration in range(iteration):
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
        ('by', 'relevancy'),
        ('order', 'desc'),
        ('page_type', 'search'),
        ('version', 2),
        ('official_mall', 1)
    )

    try:
        json = requests.get(web_url+search_endpoint, headers=headers, params=params).json()
     
        #print(json)
    except ValueError:
        print("Empty response from", web_url)
        driver.quit()
        exit()

    for item in json['items']:
        item_api.append([web_url, item['name'],item['itemid'],item['shopid'],item['price']])


    # check empty results
    if len(item_api) <= 0:
       
        print("{} NOT FOUND".format(keyword))
        return url, None
    #item_api = list(np.unique(item_api))

    dfrm = pd.DataFrame(item_api, columns=['url','name','itemid','shopid','price'])
    dfrm = dfrm.drop_duplicates()
    dfrm['keyword'] = keyword


    # get similarity string to filtering non match as a string
    dfrm['distance'] = dfrm.apply(lambda x: textdistance.levenshtein.normalized_similarity(\
                            x['name'].lower(), x['keyword'].lower()), axis=1)   
    dfrm = dfrm[dfrm['distance'] > 0.3].reset_index(drop=True)
    print(dfrm)
    if len(dfrm) <= 0:
       
        print("{} NOT FOUND IN FILTER DISTANCE".format(keyword))
        return url, None

    # get lowest price
    dfrm['price'] = pd.to_numeric(dfrm['price'])    
    dfrm = dfrm.iloc[dfrm['price'].idxmin()]
    
    print(dfrm)
    # build url from return api detail
    link_builder = search_item_builder(dfrm['url'], dfrm['name'], \
                                        dfrm['itemid'], dfrm['shopid'])
    url.append(link_builder)
    return url, (link_builder, dfrm['name'], dfrm['price'])

def search_item_builder(web_url, item_name, item_id, shop_id):
    """This method build a compact url that
    will be use when scraping
    """
    return web_url+slugify(item_name).lower()+"-i."+str(shop_id)+"."+str(item_id)



def search_shopee(driver, baseline_tup):

    plu = baseline_tup[0]
    product_name = baseline_tup[1]
    url = baseline_tup[2].strip()


    try:

        driver.get(url)


        ## CASE TO CHECK IF 
        time.sleep(random.randint(6,8))
        

        print("BEGIN MIMICKING HUMAN ACTIVITY")
        random_int = str(random.randint(-15,-5))
        driver.execute_script("window.scrollBy(0,"+random_int+");")


        print("BEGIN WAITING FOR ELEMENT PRESENCE")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.pmmxKx')))

        
        print("END WAITING FOR ELEMETN PRESENCE")

        product_name_get = driver.find_element_by_css_selector('.VCNVHn').text
        price_final_get = driver.find_element_by_css_selector('.pmmxKx').text

        try:
            price_normal_get = driver.find_element_by_css_selector('.CDN0wz').text

        except NoSuchElementException:
            price_normal_get = price_final_get


        print("RESULT ELEMENT", product_name_get, price_normal_get, price_final_get)
        print("="*50)


        price_normal_get = rupiah_format_to_number1(price_normal_get)
        price_final_get = rupiah_format_to_number1(price_final_get)


        AC_PLU = plu
        AC_SOURCE = url
        AC_PRODUCT_NAME = product_name_get.strip()
        AC_PRICE_NORMAL = price_normal_get
        AC_PRICE_FINAL = price_final_get
        AC_COMPETITOR = 'shopee'


        tup_res = (AC_PLU, AC_SOURCE, AC_PRODUCT_NAME, AC_PRICE_NORMAL, AC_PRICE_FINAL, AC_COMPETITOR)


        res_to_db(tup_res)

    except Exception as e:
        print('ERROR {}'.format(e))
        print('CANNOT GET FOR BASELINE {}'.format(baseline_tup))
        

        AC_PLU = plu
        AC_SOURCE = url
        AC_PRODUCT_NAME = None
        AC_PRICE_NORMAL = None
        AC_PRICE_FINAL = None
        AC_COMPETITOR = 'shopee'



        tup_res = (AC_PLU, AC_SOURCE, AC_PRODUCT_NAME, AC_PRICE_NORMAL, AC_PRICE_FINAL, AC_COMPETITOR)


        res_to_db(tup_res)



    return 0


def search_klikindomaret(driver, baseline_tup):

    try:
        plu = baseline_tup[0]
        product_name = baseline_tup[1]
        url = baseline_tup[2].strip()


        driver.get(url)

        time.sleep(random.randint(6,8))
        

        ## BEGIN MIMICKING HUMAN ACTIVITY   
        random_int = str(random.randint(-15,-5))
        driver.execute_script("window.scrollBy(0,"+random_int+");")
        
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="section-detailInfo"]/div/div[1]/h3')))

        
        product_name_get = driver.find_element_by_xpath('//*[@id="section-detailInfo"]/div/div[1]/h3').text
        price_get = driver.find_element_by_xpath('//*[@id="section-detailInfo"]/div/div[2]').text

    
        price_get = rupiah_format_to_number2(price_get)
        print("PRODUCT NAME GET {}".format(product_name_get))
        print("PRICE GET {}".format(price_get))
        print("="*50)


        price_normal_get = rupiah_format_to_number1(price_get[0])
        price_final_get = rupiah_format_to_number1(price_get[1])


        AC_PLU = plu
        AC_SOURCE = url
        AC_PRODUCT_NAME = product_name_get.strip()
        AC_PRICE_NORMAL = price_normal_get
        AC_PRICE_FINAL = price_final_get
        AC_COMPETITOR = 'klikindomaret'



        tup_res = (AC_PLU, AC_SOURCE, AC_PRODUCT_NAME, AC_PRICE_NORMAL, AC_PRICE_FINAL, AC_COMPETITOR)


        res_to_db(tup_res)





    except Exception as e:
        print('ERROR {}'.format(e))
        print('CANNOT GET FOR BASELINE {}'.format(baseline_tup))
        

        AC_PLU = plu
        AC_SOURCE = url
        AC_PRODUCT_NAME = None
        AC_PRICE_NORMAL = None
        AC_PRICE_FINAL = None
        AC_COMPETITOR = 'klikindomaret'



        tup_res = (AC_PLU, AC_SOURCE, AC_PRODUCT_NAME, AC_PRICE_NORMAL, AC_PRICE_FINAL, AC_COMPETITOR)


        res_to_db(tup_res)

    return 0





def search(driver, baseline_tup):
    url = baseline_tup[2]
    if url == 'https://shopee.co.id/':
        return None

    driver.get(url)
    time.sleep(8)
    product = {
        'url' : url,

    }
    # Fixed 
    try:                                            
        title = driver.find_elements_by_xpath('/html/body/div[1]/div/div[2]/div[1]/div/div[1]/div/div[1]/div[3]/div/div[1]/span')
    except NoSuchElementException: 
        title = []


    if len(title) == 0:
        try:                                        
            title = driver.find_elements_by_xpath('//*[@id="main"]/div/div[2]/div[2]/div[2]/div[1]/div[3]/div/div[1]/span')
        except NoSuchElementException:
            title = []

    if len(title) == 0:
        try:
            title = driver.find_elements_by_xpath('//*[@id="main"]/div/div[2]/div[2]/div/div[1]/div[3]/div/div[1]/span')
        except NoSuchElementException:
            title = []

    if len(title) == 0:
        try:                                        
            title = driver.find_elements_by_xpath('//*[@id="main"]/div/div[2]/div[2]/div[2]/div[3]/div[3]/div/div[1]/span')
        except NoSuchElementException:
            title = '-'
            product['title'] = title

    if len(title) == 0:
        try:
            title = driver.find_elements_by_xpath('//*[@id="main"]/div/div[2]/div[1]/div/div[2]/div/div[1]/div[3]/div/div[1]/span')
        except NoSuchElementException:
            title = '-'
            product['title'] = title



    try:                                    
        price = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[1]/div/div[1]/div/div[1]/div[3]/div/div[3]/div/div')
    except NoSuchElementException:
        price = '-'
        product['price'] = price

    if (price == '-'):
        try:                                        
            price = driver.find_element_by_xpath('//*[@id="main"]/div/div[2]/div[2]/div[2]/div[1]/div[3]/div/div[3]/div/div')
        except Exception as e:
            price = '-'
            product['price'] = price

    if (price == '-'):
        try:
            price = driver.find_element_by_xpath('//*[@id="main"]/div/div[2]/div[2]/div/div[1]/div[3]/div/div[3]/div/div')
                                                 
        except Exception as e:
            price = '-'
            product['price'] = price
                        
    if (price == '-'):
        try:                                        
            price = driver.find_element_by_xpath('//*[@id="main"]/div/div[2]/div[2]/div[2]/div[3]/div[3]/div/div[3]/div/div')
        except Exception as e:
            price = '-'
            product['price'] = price


    if (price == '-'):
        try:
            price = driver.find_element_by_xpath('//*[@id="main"]/div/div[2]/div[1]/div/div[2]/div/div[1]/div[3]/div/div[3]/div/div')
        except Exception as e:
            price = '-'
            product['price'] = price


    try:
        deskripsi = driver.find_element_by_xpath('//*[@id="main"]/div/div[2]/div[2]/div[2]/div[3]/div[2]/div[1]/div[1]/div[2]/div[2]/div/span')
    except NoSuchElementException:
        deskripsi = '-'
        product['desc'] = deskripsi

    try:
        category = driver.find_element_by_xpath('//*[@id="main"]/div/div[2]/div[2]/div[2]/div[3]/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/div/a[2]')
    except NoSuchElementException:
        category = '-'
        product['category'] = category

    try:
        subcategory = driver.find_element_by_xpath('//*[@id="main"]/div/div[2]/div[2]/div[2]/div[3]/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/div/a[3]')
    except NoSuchElementException:
        subcategory = '-'
        product['subcategory'] = subcategory

    seller = '-'
    try:
        seller = driver.find_element_by_xpath('//*[@id="main"]/div/div[2]/div[2]/div[2]/div[3]/div[1]/div[1]/div/div[1]')
    except NoSuchElementException as NEE:
        pass

    if(seller == '-'):
        try:
            seller = driver.find_element_by_css_selector('._3uf2ae')
        except NoSuchElementException as NEE:
            seller = '-'
            product['seller'] = seller

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


    if(title != '-'):
        product['title'] = title[0].text
    if(price != '-'):
        product['price'] = price.text
    if(deskripsi != '-'):
        product['desc'] = deskripsi.text
    if(category != '-'):
        product['category'] = category.text
    if(subcategory != '-'):
        product['subcategory'] = subcategory.text
    if(seller != '-'):
        product['seller'] = seller.text
    if(subsubcategory != '-'):
        product['subsubcategory'] = subsubcategory.text
    if(city != '-'):
        product['city'] = city.text
    if(terjual != '-'):
        product['sold'] = terjual.text
    if(star != '-'):
        product['star'] = star.text






    return product

def search_klik(driver, url):
    if url == 'https://shopee.co.id/':
        return None

    driver.get(url)
    time.sleep(8)
    product = {
        'url' : url,

    }
    # Fixed 
    try:
        title = driver.find_elements_by_xpath('//*[@id="section-detailInfo"]/div/div[1]/h3')
    except NoSuchElementException: 
        title = '-'
        product['title'] = title

    try:
        price = driver.find_element_by_xpath('//*[@id="section-detailInfo"]/div/div[2]')
    except NoSuchElementException:
        price = '-'
        product['price'] = price

    try:
        deskripsi = driver.find_element_by_xpath('//*[@id="section-detailInfo"]/div/div[4]/div[2]/div/span')
    except NoSuchElementException:
        deskripsi = '-'
        product['desc'] = deskripsi

    try:
        category = driver.find_element_by_xpath('//*[@id="main"]/div/div[2]/div[2]/div[2]/div[3]/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/div/a[2]')
    except NoSuchElementException:
        category = '-'
        product['category'] = category

    try:
        subcategory = driver.find_element_by_xpath('//*[@id="main"]/div/div[2]/div[2]/div[2]/div[3]/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/div/a[3]')
    except NoSuchElementException:
        subcategory = '-'
        product['subcategory'] = subcategory

    seller = '-'
    try:
        seller = driver.find_element_by_xpath('//*[@id="section-detailInfo"]/div/div[1]/span[1]/span')
    except NoSuchElementException as NEE:
        pass

    if(seller == '-'):
        try:
            seller = driver.find_element_by_css_selector('div.each-section:nth-child(1) > span:nth-child(2) > span:nth-child(2)')
        except NoSuchElementException as NEE:
            seller = '-'
            product['seller'] = seller

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


    if(title != '-'):
        product['title'] = title[0].text
    if(price != '-'):
        product['price'] = price.text
    if(deskripsi != '-'):
        product['desc'] = deskripsi.text
    if(category != '-'):
        product['category'] = category.text
    if(subcategory != '-'):
        product['subcategory'] = subcategory.text
    if(seller != '-'):
        product['seller'] = seller.text
    if(subsubcategory != '-'):
        product['subsubcategory'] = subsubcategory.text
    if(city != '-'):
        product['city'] = city.text
    if(terjual != '-'):
        product['sold'] = terjual.text
    if(star != '-'):
        product['star'] = star.text

    return product
