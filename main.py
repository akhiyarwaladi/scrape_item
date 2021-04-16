from with_selenium import browse_with_selenium as sel
import pandas as pd
import json
import os

SHOPEE_URL = "https://shopee.co.id/"
SEARCH_ENDPOINT = "api/v2/search_items/"
SEARCH_ITERATION = 3   # Number of page to browse

#parent_path = '/home/server/gli-data-science/akhiyar'
parent_path = '/home/rahasia/gli'
def main():
    """Using selenium to scrape Shopee """

    driver = sel.init()


    for idx, row in pd.read_excel(os.path.join(parent_path, 'stok_tgl_13.xlsx'))[5:]\
                        .iloc[:,0:2].reset_index(drop=True).iterrows():
        SEARCH_KEYWORD = row.iloc[1]

        print(SEARCH_KEYWORD)
        SAVED_FILE = os.path.join(parent_path, "product_scrape/{}.json".format(SEARCH_KEYWORD))
        products=[]
    

        urls = sel.url_harvest_by_keyword(
                                driver=driver,
                                web_url=SHOPEE_URL, 
                                search_endpoint=SEARCH_ENDPOINT, 
                                keyword=SEARCH_KEYWORD,
                                iteration=SEARCH_ITERATION)

        for idx, url in enumerate(urls):
            product = sel.search(driver=driver, url=url)
            if product is None:
                print("CANNOT GET DETAIL {}".format(url))
                product = {}

            
            product['plu_alfa'] = row.iloc[0]
            products.append(product)


            with open(SAVED_FILE, 'w', encoding='utf-8') as f:
                json.dump(products, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
