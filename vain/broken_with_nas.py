import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlsplit, urlunsplit, quote
from concurrent.futures import ThreadPoolExecutor
import os

visited_pages = set()

OUTPUT_FILE = "output_for_broken_with_nas.txt"
if os.path.exists(OUTPUT_FILE):
    os.remove(OUTPUT_FILE)

def log_to_output(content):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(content + "\n")

def encode_url_if_needed(url):
    parts = urlsplit(url)
    encoded_path = quote(parts.path)
    return urlunsplit((parts.scheme, parts.netloc, encoded_path, parts.query, parts.fragment))

def get_all_links_from_page(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return [], []

        soup = BeautifulSoup(response.text, 'html.parser')
        image_links = [urljoin(url, img['src']) for img in soup.find_all('img', src=True)]
        page_links = [urljoin(url, a['href']) for a in soup.find_all('a', href=True)]

        # Filter to stay within the same website
        domain = urlparse(url).netloc
        page_links = [link for link in page_links if urlparse(link).netloc == domain]

        # Validate and fix image URLs
        valid_image_links = []
        for img_url in image_links:
            if " " in img_url or not img_url.isascii():
                log_to_output(f"[Non-ASCII or space in image URL on {url}] → {img_url}")
                fixed_url = encode_url_if_needed(img_url)
                log_to_output(f"[Auto-encoded URL] → {fixed_url}")
                valid_image_links.append(fixed_url)
            else:
                valid_image_links.append(img_url)

        return valid_image_links, page_links

    except Exception as e:
        log_to_output(f"[Error fetching page] {url}: {e}")
        return [], []

def crawl_website(start_url):
    to_visit = [start_url]
    all_image_links = []

    while to_visit:
        url = to_visit.pop()
        if url in visited_pages:
            continue
        visited_pages.add(url)
        print(f"[Crawling] {url}")
        log_to_output(f"\n[Crawling] {url}")
        images, links = get_all_links_from_page(url)
        all_image_links.extend(images)
        to_visit.extend([link for link in links if link not in visited_pages])
    
    return list(set(all_image_links))  # Remove duplicates

def check_image_link(url):
    try:
        response = requests.head(url, timeout=5)
        if response.status_code >= 400:
            return url, response.status_code
    except Exception as e:
        return url, str(e)
    return None

def check_broken_images(image_urls):
    broken = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(check_image_link, image_urls)
        for result in results:
            if result:
                broken.append(result)
    return broken

def main(websites):
    for site in websites:
        print(f"\n[Scanning Website] {site}")
        log_to_output(f"\n==============================")
        log_to_output(f"[Scanning Website] {site}")
        log_to_output(f"==============================")
        global visited_pages
        visited_pages = set()  # Reset for each site
        image_urls = crawl_website(site)
        log_to_output(f"[Total Images Found] {len(image_urls)}")
        broken_images = check_broken_images(image_urls)
        log_to_output(f"[Broken Images Found] {len(broken_images)}")
        for url, error in broken_images:
            log_to_output(f" - {url} --> {error}")
        log_to_output("***************************************")

    print("\n[Scan Complete] Check 'output_for_broken_with_nas.txt' for results.")

if __name__ == "__main__":
    # Storing the websites as a Python list with full https:// links
    websites = [
    # "https://albania-evisa.org",
    # "https://azerbaijan-e-visa.com",
    # "https://bahrain-evisa.com",
    # "https://benin-e-visa.com",
    # "https://bolivia-evisa.com",
    # "https://bosnia-evisa.com",
    # "https://botswana-visa.com",
    # "https://bulgaria-evisa.com",
    # "https://cameroon-evisa.com",
    # "https://chile-evisa.com",
    # "https://congo-evisa.com",
    # "https://djibouti-evisa.com",
    # "https://e-visa-cambodia.com",
    # "https://e-visa-southafrica.com",
    # "https://egypt-e-visa.org",
    # "https://egypt-eta.com",
    # "https://eta-canada.info",
    # "https://eta-cuba.com",
    # "https://ethiopia-e-visa.com",
    # "https://evisa-madagascar.com",
    # "https://evisa-moldova.com",
    # "https://evisa-myanmar.com",
    # "https://evisa-to-kenya.org",
    # "https://evisa-to-saudi-arabia.com",
    # "https://georgia-e-visa.com",
    # "https://india-e-visa.net",
    # "https://india-s-travel.com",
    # "https://indonesia-e-visa.com",
    # "https://japanevisa.net",
    # "https://lao-evisa.com",
    # "https://libya-e-visa.com",
    # "https://malaysia-e-visa.com",
    # "https://mexico-e-visa.com",
    # "https://morocco-e-visas.com",
    # "https://nigeria-e-visa.com",
    # "https://nz-eta.info",
    # "https://philippines-evisa.org",
    # "https://romania-e-visa.com",
    # "https://russian-e-visa.com",
    # "https://south-korea-evisa.com",
    # "https://tanzania-e-visas.com",
    # "https://thailand-e-visas.com",
    # "https://tunisia-e-visa.com",
    # "https://turkey-e-visas.com",
    # "https://united-kingdom-visa.com",
    # "https://vietnam-e-visas.com",
    # "https://visa-armenia.com",
    # "https://visa-kuwait.com",
    # "https://visa-qatar.com",
    # "https://zambia-visa.com",
    # "https://zimbabwe-visa.com"
    "https://turkey-e-visas.com"
]

# websites[:5]  # Show a sample of the list to confirm it stored correctly

    main(websites)
