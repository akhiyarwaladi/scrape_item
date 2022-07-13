from with_selenium import browse_with_selenium as sel
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd
# +
import gspread
import gspread_dataframe as gd
import gspread_formatting as gf
from google.oauth2.service_account import Credentials


scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']


saf = '/home/server/gli-data-science/akhiyar/dashboard_job/alfagift-report-907cce167320.json'
credentials = Credentials.from_service_account_file(saf, scopes=scope)

gc = gspread.authorize(credentials)




ws = gc.open_by_key("1ss-Upt9I43g4YpfieJfALcuv5S0Az3V6pabEZ4sESRg").worksheet("Sheet1")


df_astro = pd.DataFrame(ws.get_all_values())
df_astro = df_astro[0:]

new_header = df_astro.iloc[0] #grab the first row for the header
df_astro = df_astro[1:] #take the data less the header row
df_astro.columns = new_header #set the header row as the df header
# -


import pandas as pd
import json
import os
import sys
sys.path.append('/home/server/gli-data-science')
import lib_3d
import time
import ds_db


q = """
SELECT 
    AC_PLU, 
    AC_SOURCE, 
    AC_PRODUCT_NAME,  
    AC_PRICE_NORMAL, 
    AC_PRICE_FINAL, 
    AC_COMPETITOR,
    AC_UPDATE_DATE
FROM 
    ALFAGIFT_COMPETITIVENESS ac
WHERE AC_PRICE_FINAL IS NULL
ORDER BY AC_UPDATE_DATE ASC

"""

con = ds_db.connect_alfabi()
df_astro = pd.read_sql_query(q, con)
con.close()






SHOPEE_URL = "https://shopee.co.id/"
SEARCH_ENDPOINT = "api/v2/search_items/"
SEARCH_ITERATION = 3   # Number of page to browse

parent_path = '/home/server/gli-data-science/akhiyar/scrape_product'
# parent_path = '/home/rahasia/gli'






def main():
    """Using selenium to scrape Shopee """

    ## to login 
    
    driver = sel.init()
    driver.get('https://shopee.co.id/buyer/login')

    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[2]/div/div/form/div/div[2]/div[5]/div[2]/button[2]')))
        driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/form/div/div[2]/div[5]/div[2]/button[2]').click()
        time.sleep(5)
        driver.quit()

    except:
        driver.quit()
        pass
    


    with open(os.path.join(parent_path,'irregular_link.txt'), 'w') as li_link:    
        for sheet_id in range(0,1,1):
            # sheet_id = 1
            #if sheet_id == 0 or sheet_id == 1:
            #    continue
#             for idx, row in pd.read_excel(os.path.join(parent_path,\
#                             '20210421_TagI_Competitiveness_2.xlsx'), sheet_name=sheet_id)\
#                             .iterrows():
            for idx,row in df_astro.iterrows():
                plu_alfa = row['AC_PLU']
                SEARCH_KEYWORD = row['AC_PRODUCT_NAME']
                url = row['AC_SOURCE']
                competitor = row['AC_COMPETITOR']   
                driver = sel.init()
                #### VERSION BEFORE 
                # SAVED_FILE = os.path.join(parent_path, "product_scrape_{}/{}.json"\
                #             .format(sheet_id, plu_alfa))
                # products=[]
                ####



                #plu_alfa = row.iloc[0]
                #SEARCH_KEYWORD = row.iloc[1]
                #url = row.iloc[2]
                
                print("BASELINE", plu_alfa, SEARCH_KEYWORD, url, competitor)
                print("="*50)

                baseline_tup = (plu_alfa, SEARCH_KEYWORD, url)


                



                ######## if we dont have url we must search in database
                # urls, det_urls = sel.url_harvest_by_keyword(
                #                         driver=driver,
                #                         web_url=SHOPEE_URL, 
                #                         search_endpoint=SEARCH_ENDPOINT, 
                #                         keyword=SEARCH_KEYWORD,
                #                         iteration=SEARCH_ITERATION)

                # # for idx, url in enumerate(urls):
                # if len(urls) <= 0:
                #     url = 'https://shopee.co.id/'
                # else:
                #     url = urls[0]
                # print(url)
                #######################################################
                print("SHEET ID NOW {}".format(sheet_id))
                try:
                    if competitor == 'shopee':
                        product = sel.search_shopee(driver=driver, baseline_tup=baseline_tup)
                    else:
                        product = sel.search_klikindomaret(driver=driver, baseline_tup=baseline_tup)



                    ###### VERSION BEFORE
                    # # failed to get detail item in product page
                    # if product is None:
                    #     if det_urls is None:
                    #         print("CANNOT GET DETAIL {}".format(url))
                    #         product = {}
                    #     # if we already get mini detail in api but fail in big detail product page
                    #     else:
                    #         print("WE HAVE API DETAIL \n{}".format(det_urls))
                    #         product = {
                    #             'url' : det_urls[0],
                    #             'title' : det_urls[1],
                    #             'price' : str(det_urls[2])
                    #         }

                    # # get our plu as a key to search item
                    # product['plu_alfa'] = plu_alfa
                    # if (product['title'] == '-') or (product['price'] == '-'):
                    #     li_link.write("fail({})\n({})\n({})".format(plu_alfa, SEARCH_KEYWORD, str(url))+ '\n')
                    #     lib = lib_3d.desan()

                    #     preceiver = "akhiyar.waladi@gli.id"
                    #     print(preceiver)

                    #     psubject = ''
                    #     pbody = """
                    #        Please check {} \n\n {}
                    #     """.format(datetime.now().date().strftime('%d%b%Y'), product)

                    #     lib.kirim_email_noreply(preceiver, psubject, pbody, spath_susu)
                    #     continue
                    # ## if all detail not '-' (empty)
                    # products.append(product)


                    # with open(SAVED_FILE, 'w', encoding='utf-8') as f:
                    #     json.dump(products, f, ensure_ascii=False, indent=4)
                    ###### END OF VERSION BEFORE

                except Exception as e:
                    print('{} --> {}'.format(e, SEARCH_KEYWORD))
                    
                    li_link.write("dead({})\n({})\n({})".format(plu_alfa, SEARCH_KEYWORD, str(url))+ '\n')



                finally:
                    driver.quit() #This runs even if the code under try crashes
                    
    li_link.close()

if __name__ == "__main__":
    main()
