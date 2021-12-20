import os
import re
import csv
import time
import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver

category_page_url = 'https://sbermegamarket.ru/catalog/korma-dlya-koshek/'

wFile = open("sber_res.csv", mode = "w", encoding = 'utf-8')

names = ["Наименование", "Цена", "Характеристики",
         "Продавец", "Ссылка на производителя", 
         "Ссылки на картинки", "Имена картинок"]

file_writer = csv.DictWriter(wFile, delimiter = ';', lineterminator = '\n', fieldnames = names)
file_writer.writeheader()

try:
    os.mkdir('img')
except Exception as e:
    print(e)
    pass

def get_product_urls(category_url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")

    driver = webdriver.Chrome(
        executable_path=os.getcwd() + '/chromedriver.exe', 
        options=options
    )

    product_urls = list()

    try:
        driver.get(category_url)
        bso = bs(driver.page_source, 'html.parser')
        product_list = bso.find_all('div', {'class': 'catalog-item__mobile-title-container'})

        for product in product_list:
            product_urls.append('https://sbermegamarket.ru/' + product.find('div').find('a')['href'])

    except Exception as e:
        print(e)
    finally:
        driver.delete_all_cookies()
        driver.close()
        driver.quit()
        return product_urls

def parse_product_sber(product_url):

    response = requests.get(product_url)

    good_specs = list()
    good_photo_urls = list()
    photo_names = list()

    bso = bs(response.content, 'html.parser')

    try:
        name = bso.find('header', {'class': 'pdp-header__header'}).find('h1').text
    except Exception as e:
        name = 'no_data'
        print(e)

    try:
        dirname = re.sub('[^A-Za-z0-9А-Яа-я]', '_', name)
        os.mkdir('img/' + dirname)
    except Exception as e:
        print(e)
        pass

    try:
        price = bso.find('div', {'class': 'price__final'}).text
    except Exception as e:
        price = 'no_data'
        print(e) 
    
    try:
        specs = bso.find('ul', {'class': 'pdp-attrs-block'}).find_all('li')
        for spec in specs:
            good_specs.append(spec.text)
    except Exception as e:
        good_specs.append('no_data')
        print(e) 

    try:
        customer = bso.find('a', {'class': 'pdp-offer-block__merchant-link'}).text
    except Exception as e:
        customer = 'no_data'
        print(e)

    try:
        customer_url = bso.find('a', {'class': 'pdp-offer-block__merchant-link'})['href']
    except Exception as e:
        customer_url = 'no_data'
        print(e)

    try:

        photo_urls = bso.find_all('a', {'class': 'gallery__thumb'})

        for photo_url in photo_urls:
            good_photo_urls.append(photo_url.find('img')['src'])

            photo_names.append(good_photo_urls[len(good_photo_urls) - 1][good_photo_urls[len(good_photo_urls) - 1].rfind('/'):])

            img_data = requests.get(good_photo_urls[len(good_photo_urls) - 1]).content

            with open('img/'+ dirname + '/' + photo_names[len(photo_names) - 1][2:], 'wb') as fw:
                fw.write(img_data)

    except Exception as e:
        good_photo_urls.append('no_data')
        print(e)
        

    file_writer.writerow({"Наименование": name, "Цена": price, "Характеристики": good_specs,
                          "Продавец": customer, "Ссылка на производителя": customer_url, 
                          "Ссылки на картинки": good_photo_urls, "Имена картинок": photo_names})


if __name__ == "__main__":
    start_time = time.time()

    prod_urls = get_product_urls(category_page_url)
    for prod_url in prod_urls:
        parse_product_sber(prod_url)

    print("By " + str(time.time() - start_time) + " seconds")
    