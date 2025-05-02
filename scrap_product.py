import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class AmazonScraper:
    def __init__(self, product_name):
        self.product = product_name
        self.base_url = f"https://www.amazon.in/s?k={self.product.replace(' ', '+')}"
        self.sort_options = {
            "Price: High to Low": "price-desc-rank",
            "Avg. Customer Review": "review-rank",
            "Best Seller": "salesrank"
        }
        self.all_data = []

        # Setup headless browser
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("user-agent=Mozilla/5.0")
        self.driver = webdriver.Chrome(options=options)

    def get_product_links(self):
        time.sleep(1)
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        link_tags = soup.find_all("a", class_="a-link-normal s-line-clamp-2 s-link-style a-text-normal")
        result = []
        for tag in link_tags:
            href = tag.get("href")
            if href and href.startswith("/"):
                clean_href = href.split("/ref")[0]
                full_link = "https://www.amazon.in" + clean_href
                result.append(full_link)
        return result

    def extract_product_details(self, product_url):
        self.driver.get(product_url)
        time.sleep(1)
        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        # Title
        try:
            title = soup.find("span", class_="a-size-large product-title-word-break").text.strip()
        except:
            title = ""

        # Price
        try:
            price = soup.find("span", class_="a-price-whole").text.strip()
        except:
            price = ""

        # Rating
        rating = ""
        spans = soup.find_all("span", class_="a-size-base a-color-base")
        for span in spans:
            if span.text.strip().replace('.', '', 1).isdigit():
                rating = span.text.strip()
                break

        # Review count
        try:
            review_count = soup.find("span", id="acrCustomerReviewText").text.strip()
        except:
            review_count = ""

        # Image URL
        img_link = ""
        image_div = soup.find("div", id="imgTagWrapperId")
        if image_div:
            img_tag = image_div.find("img")
            if img_tag:
                img_link = img_tag.get("data-old-hires") or img_tag.get("src")

        return {
            "title": title,
            "price": price,
            "rating": rating,
            "review_count": review_count,
            "image_url": img_link,
            "product_url": product_url
        }

    def scrape_all(self):
        for category_name, sort_value in self.sort_options.items():
            print(f"\nExtracting for: {category_name}")
            sorted_url = f"{self.base_url}&s={sort_value}"
            self.driver.get(sorted_url)

            product_links = self.get_product_links()
            print(f"Found {len(product_links)} products in: {category_name}")

            for link in product_links:
                details = self.extract_product_details(link)
                details["category"] = category_name
                self.all_data.append(details)

        self.driver.quit()

    def save_to_csv(self, filename="amazon_products.csv"):
        df = pd.DataFrame(self.all_data)
        df.to_csv(filename, index=False)
        print(f"\n✅ Data saved to '{filename}'")
