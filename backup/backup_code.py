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