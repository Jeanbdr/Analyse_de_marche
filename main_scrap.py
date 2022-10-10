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
header = [
    "title",
    "review_rating",
    "universal_product_codes",
    "price_including_tax",
    "price_excluding_tax",
    "number_available",
    "category",
    "product_description",
    "product_page_url",
    "image_url",
]

# Date import
today = date.today()
d1 = today.strftime("%d_%m_%y")

# Creation of directory
main_dir = d1 + "_Books"
os.mkdir(main_dir)

# Directory for picture
pic_dir = "Book_Cover"
img_path = os.path.join(main_dir, pic_dir)
os.mkdir(img_path)

# Directory for csv
cs_dir = "Book_info"
info_path = os.path.join(main_dir, cs_dir)
os.mkdir(info_path)


def scrape_home():
    nav_home = soup.find("ul", {"class": "nav"}).find_all("a")[1:]
    for category in nav_home:
        # Get category name
        category_name = category.text.strip()
        # Get category link
        category_link = category.get("href")
        # Modify links for later use
        category_link = urljoin("http://books.toscrape.com/", category_link)
        # Launching scrape category function
        scrape_category(category_link, category_name)
    return category_link, category_name


def scrape_category(category_link, category_name):
    response = requests.get(category_link)
    soup = BeautifulSoup(response.content, "html.parser")
    # Looking for a possible next page
    next_page = soup.find("li", class_="current")
    # Splitting 'next page' in chunks and get the needed element
    total_page = int(str(next_page).split()[5]) if next_page else 1
    # Creation of csv (+add path)
    table_name = os.path.join(info_path, f"{category_name}.csv")
    with open(table_name, "w", encoding="UTF8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        # Read into different page to get all links
        for page_number in range(1, total_page + 1):
            if page_number == 1:
                page_link = category_link
            else:
                page_link = urljoin(category_link, f"page-{page_number}.html")
            response = requests.get(page_link)
            soup = BeautifulSoup(response.content, "html.parser")
            book_titles = soup.find_all("h3")
            for h3 in book_titles:
                book_link = urljoin(category_link, h3.find("a")["href"])
                book_data = scrape_book(book_link)
                filename = os.path.join(img_path, book_data[0].replace("/", "") + ".jpg")
                urllib.request.urlretrieve(book_data[-1], filename)
                writer.writerow(book_data)


def scrape_book(book_link):
    # Url requests and parsing
    response = requests.get(book_link)
    soup = BeautifulSoup(response.content, "html.parser")
    # Get title
    title = soup.find("h1").get_text()
    # Get data
    table_lines = soup.findAll("td")
    upc = table_lines[0]
    untaxed_price = table_lines[2]
    taxed_price = table_lines[3]
    availability = table_lines[5]
    # Get description
    if soup.find("div", {"id": "product_description"}):
        raw_description = soup.find("div", {"id": "product_description"}).find_next("p")
        description = raw_description.get_text()
    else:
        description = "No description found"
    # Get category
    category = soup.find("ul", class_="breadcrumb").find_all("a")[-1]
    # Get image
    img_src = soup.find("img").get("src")
    img_url = urljoin(book_link, img_src)
    # Get rating
    rating = soup.find("p", class_="star-rating").get("class")[1]
    # Return of value for csv purpose
    return (
        title,
        rating + " stars",
        upc.get_text(),
        taxed_price.get_text(),
        untaxed_price.get_text(),
        availability.get_text(),
        category.get_text(),
        description,
        book_link,
        img_url,
    )


scrape_home()
