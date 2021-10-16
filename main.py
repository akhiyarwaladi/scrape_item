from with_selenium import browse_with_selenium as sel
import pandas as pd
import json
import os
import sys
sys.path.append('/home/server/gli-data-science')
import lib_3d

SHOPEE_URL = "https://shopee.co.id/"
SEARCH_ENDPOINT = "api/v2/search_items/"
SEARCH_ITERATION = 3   # Number of page to browse

parent_path = '/home/server/gli-data-science/akhiyar/scrape_product'
# parent_path = '/home/rahasia/gli'
def main():
    """Using selenium to scrape Shopee """

    driver = sel.init()
    with open(os.path.join(parent_path,'irregular_link.txt'), 'w') as li_link:    
        for sheet_id in range(0,4,1):
            # sheet_id = 1
            #if sheet_id == 0 or sheet_id == 1 or sheet_id == 2:
            #    continue
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


                #SEARCH_KEYWORD = 'Sunlight Professional Sabun Cuci Piring Cair Jeruk Nipis 5 L Jerigen'
                #url = 'https://shopee.co.id/Sunlight-Sabun-Cuci-Piring-Cair-Professional-Jeruk-Nipis-Jerigen-5000-ml-i.276953550.6139557435'
                #plu_alfa = 425949
                
                
                SAVED_FILE = os.path.join(parent_path, "product_scrape_{}/{}.json"\
                            .format(sheet_id, plu_alfa))


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
                    if sheet_id == 0 or sheet_id == 3:
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
                    if (product['title'] == '-') or (product['price'] == '-'):
                        li_link.write("fail({})\n({})\n({})".format(plu_alfa, SEARCH_KEYWORD, str(url))+ '\n')
                        lib = lib_3d.desan()

                        preceiver = "akhiyar.waladi@gli.id"
                        print(preceiver)

                        psubject = ''
                        pbody = """
                           Please check {} \n\n {}
                        """.format(datetime.now().date().strftime('%d%b%Y'), product)

                        lib.kirim_email_noreply(preceiver, psubject, pbody, spath_susu)
                        continue
                    ## if all detail not '-' (empty)
                    products.append(product)


                    with open(SAVED_FILE, 'w', encoding='utf-8') as f:
                        json.dump(products, f, ensure_ascii=False, indent=4)


                except Exception as e:
                    print('{} --> {}'.format(e, SEARCH_KEYWORD))
                    
                    li_link.write("dead({})\n({})\n({})".format(plu_alfa, SEARCH_KEYWORD, str(url))+ '\n')
                    
    li_link.close()

if __name__ == "__main__":
    main()
