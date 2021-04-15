from with_selenium import browse_with_selenium as sel
import json

SHOPEE_URL = "https://shopee.co.id/"
SEARCH_ENDPOINT = "api/v2/search_items/"
#SEARCH_ENDPOINT = 'mall/search'
SEARCH_KEYWORD = "promina marie roll 150g"
SEARCH_ITERATION = 2   # Number of page to browse
SAVED_FILE = "data.json"

def main():
    """Using selenium to scrape Shopee """
    products=[]

    driver = sel.init()
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
