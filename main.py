from with_selenium import browse_with_selenium as sel
import pandas as pd
import json
import os

SHOPEE_URL = "https://shopee.co.id/"
SEARCH_ENDPOINT = "api/v2/search_items/"
SEARCH_ITERATION = 3   # Number of page to browse

parent_path = '/home/server/gli-data-science/akhiyar/scrape_product'
# parent_path = '/home/rahasia/gli'
def main():
    """Using selenium to scrape Shopee """

    driver = sel.init()
    with open(os.path.join(parent_path,'dead_link.txt'), 'w') as li_link:    
        for sheet_id in range(0,3,1):
            #sheet_id = 2

            for idx, row in pd.read_excel(os.path.join(parent_path,\
                            '20210421_TagI_Competitiveness.xlsx'), sheet_name=sheet_id)\
                            .iterrows():
                products=[]


                SEARCH_KEYWORD = row.iloc[1]
                url = row.iloc[2]
                plu_alfa = row.iloc[0]
                print(SEARCH_KEYWORD)
                print(url)
                print(plu_alfa)      


                # SEARCH_KEYWORD = 'Similac GainPlus 850 g (1-3 tahun) Susu Pertumbuhan'
                # url = 'https://shopee.co.id/Dougo-Minyak-Canola-100-1000ML-i.40341578.1683845867'
                # plu_alfa = 234331
                
                
                SAVED_FILE = os.path.join(parent_path, "product_scrape_{}/{}.json"\
                            .format(sheet_id, SEARCH_KEYWORD))


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

                try:
                    if sheet_id == 0:
                        product = sel.search(driver=driver, url=url)
                    else:
                        product = sel.search_klik(driver=driver, url=url)
                    # failed to get detail item in product page
                    if product is None:
                        if det_urls is None:
                            print("CANNOT GET DETAIL {}".format(url))
                            product = {}
                        # if we already get mini detail in api but fail in big detail product page
                        else:
                            print("WE HAVE API DETAIL \n{}".format(det_urls))
                            product = {
                                'url' : det_urls[0],
                                'title' : det_urls[1],
                                'price' : str(det_urls[2])
                            }

                    # get our plu as a key to search item
                    product['plu_alfa'] = plu_alfa
                    products.append(product)

                    print(products)

                    with open(SAVED_FILE, 'w', encoding='utf-8') as f:
                        json.dump(products, f, ensure_ascii=False, indent=4)


                except Exception as e:
                    print('{} --> {}'.format(e, SEARCH_KEYWORD))
                    
                    li_link.write("({})\n({})".format(SEARCH_KEYWORD, str(url))+'\n')
                    
    li_link.close()

if __name__ == "__main__":
    main()
