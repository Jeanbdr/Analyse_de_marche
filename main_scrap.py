# import des modules
import requests
import csv
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import urllib.request
from datetime import date

# Request and parse main url
url = 'http://books.toscrape.com/index.html'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# List of header for csv
header = ['title', 'review_rating', 'universal_product_code (upc)', 'price_including_tax',
          'price_excluding_tax', 'number_available', 'category', 'product_description',
          'product_page_url', 'image_url']

# Date import
today = date.today()
d1 = today.strftime('%d_%m_%y')

# Creation of directory
main_dir = d1 + '_Books'
parent_dir = '../../../Documents'
path = os.path.join(parent_dir, main_dir)
os.mkdir(path)

# Directory for picture
pic_dir = "Book_Cover"
par_dir = path
img_path = os.path.join(par_dir, pic_dir)
os.mkdir(img_path)

# Directory for csv
cs_dir = 'Book_info'
info_path = os.path.join(path, cs_dir)
os.mkdir(info_path)


def scrape_home():
    nav_home = soup.find('ul', {'class': 'nav'}).find_all('a')[1:3]
    for categories in nav_home:
        # Get category name
        category_name = (categories.text.strip())
        # Get category link
        category_link = categories.get('href')
        # Modify links for later use
        cat_links = urljoin('http://books.toscrape.com/', category_link)
        # Launching scrape category function
        scrape_category(cat_links, category_name)
    return(cat_links, category_name)


def scrape_category(cat_links, category_name):
    solo_response = requests.get(cat_links)
    soup = BeautifulSoup(solo_response.content, 'html.parser')
    # Looking for a possible next page
    next_page = (soup.find('li', class_='current'))
    if next_page is None:
        page_content = soup.find_all('h3')
        # Creation of csv (+ add path)
        table = category_name + '.csv'
        table_name = os.path.join(info_path, table)
        with open(table_name, 'a', encoding='UTF8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            # Looking for content in category with one page
            for h3 in page_content:
                raw_links = h3.find('a')['href'].replace('../', '')
                book_solo_link = 'http://books.toscrape.com/catalogue/' + raw_links
                for link in book_solo_link:
                    def scrape_book(book_solo_link):
                        # Get a book url
                        book_url = book_solo_link
                        # Url requests and parsing
                        response = requests.get(book_url)
                        soup = BeautifulSoup(response.content, 'html.parser')
                        # Get title
                        title = soup.find('h1').get_text()
                        # Get data
                        table_lines = soup.findAll('td')
                        upc = table_lines[0]
                        untaxed_price = table_lines[2]
                        taxed_price = table_lines[3]
                        availability = table_lines[5]
                        # Get description
                        if soup.find('div', {'id': 'product_description'}):
                            description = soup.find('div', {'id': 'product_description'}).find_next('p')
                        else:
                            description = "No description found"
                        # Get category
                        category = soup.find('ul', class_='breadcrumb').find_all('a')[-1]
                        # Get image and put them in a directory
                        picture = soup.find("img").get('src').replace('../', '')
                        pic = "http://books.toscrape.com/" + picture
                        filename = os.path.join(img_path, title + '.jpg')
                        image1 = urllib.request.urlretrieve(pic, filename)
                        # Get rating
                        rating = soup.find('p', class_='star-rating').get("class")[1]
                        # Return of value for csv purpose
                        return(title, rating + ' stars', upc.get_text(), taxed_price.get_text(),
                               untaxed_price.get_text(), availability.get_text(), category.get_text(),
                               description.get_text(), book_url, pic)
                # Add value to csv
                data_solo = scrape_book(book_solo_link)
                writer.writerow(data_solo)
    # If next page available this part will be use
    else:
        # Splitting 'next page' in chunks and get the needed element
        page = str(next_page).split()[5]
        # Change of page value into an integer
        total_page = int(page)
        # Creation of csv (+add path)
        table = category_name + '.csv'
        table_name = os.path.join(info_path, table)
        with open(table_name, 'a', encoding='UTF8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            # Read into different page to get all links
            for x in range(1, total_page + 1):
                cat_links_modify = cat_links.replace('/index.html', '')
                raw_multi_link = cat_links_modify + '/page-' + str(x) + '.html'
                clean_links_multi = raw_multi_link.replace('page-1.html', 'index.html')
                multi_response = requests.get(clean_links_multi)
                soup = BeautifulSoup(multi_response.content, 'html.parser')
                multipage_content = soup.find_all('h3')
                for h3 in multipage_content:
                    link_raw = h3.find('a')['href'].replace('../', '')
                    book_multi_link = 'http://books.toscrape.com/catalogue/' + link_raw
                    for links in book_multi_link:
                        def scrape_book(book_multi_link):
                            # Get a book url
                            book_url = book_multi_link
                            # Url requests and parsing
                            response = requests.get(book_url)
                            soup = BeautifulSoup(response.content, 'html.parser')
                            # Get title
                            title = soup.find('h1').get_text()
                            # Get data
                            table_lines = soup.findAll('td')
                            upc = table_lines[0]
                            untaxed_price = table_lines[2]
                            taxed_price = table_lines[3]
                            availability = table_lines[5]
                            # Get description
                            if soup.find('div', {'id': 'product_description'}):
                                description = soup.find('div', {'id': 'product_description'}).find_next('p')
                            else:
                                description = "No description found"
                            # Get category
                            category = soup.find('ul', class_='breadcrumb').find_all('a')[-1]
                            # Get image
                            picture = soup.find("img").get('src').replace('../', '')
                            pic = "http://books.toscrape.com/" + picture
                            filename = os.path.join(img_path, title + '.jpg')
                            image1 = urllib.request.urlretrieve(pic, filename)
                            # Get rating
                            rating = soup.find('p', class_='star-rating').get("class")[1]
                            # Return the value
                            return(title, rating + ' stars', upc.get_text(), taxed_price.get_text(),
                                   untaxed_price.get_text(), availability.get_text(), category.get_text(),
                                   description.get_text(), book_url, pic)
                    data_multi = scrape_book(book_multi_link)
                    writer.writerow(data_multi)


scrape_home()
