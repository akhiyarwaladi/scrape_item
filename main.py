from with_selenium import browse_with_selenium as sel
import pandas as pd
import json

SHOPEE_URL = "https://shopee.co.id/"
SEARCH_ENDPOINT = "api/v2/search_items/"
#SEARCH_ENDPOINT = 'mall/search'

SEARCH_ITERATION = 1   # Number of page to browse


def main():
    """Using selenium to scrape Shopee """

    driver = sel.init()


    for SEARCH_KEYWORD in list(pd.read_excel('/home/server/gli-data-science/akhiyar/stok_tgl_13.xlsx')[5:].iloc[:,1])
        SAVED_FILE = "/home/server/gli-data-science/akhiyar/product_scrape/{}.json".format(SEARCH_KEYWORD)
        products=[]
        urls = sel.url_harvest_by_keyword(
                                driver=driver,
                                web_url=SHOPEE_URL, 
                                search_endpoint=SEARCH_ENDPOINT, 
                                keyword=SEARCH_KEYWORD,
                                iteration=SEARCH_ITERATION)
        for idx, url in enumerate(urls):
            product= sel.search(driver=driver, url=url)
            products.append(product)


            with open(SAVED_FILE, 'w', encoding='utf-8') as f:
                json.dump(products, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
