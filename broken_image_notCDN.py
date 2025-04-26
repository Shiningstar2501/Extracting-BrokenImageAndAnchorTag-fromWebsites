import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse, quote
import os

# Global stores
visited_pages = set()
checked_image_urls = set()
output_file = None

# Create output directory
output_folder = "BrokenImageReports"
os.makedirs(output_folder, exist_ok=True)

# Set log file per domain (country)
def set_output_file(start_url):
    global output_file
    # Use the domain name as the country name
    domain = urlparse(start_url).netloc.replace(".", "-")
    output_file = os.path.join(output_folder, f"{domain}-broken-images.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"[Scanning Images for] {start_url}\n\n")

# Log to console and file
def log(message):
    print(message)
    with open(output_file, "a", encoding="utf-8") as f:
        f.write(message + "\n")

# Safely encode URL paths
def sanitize_url(url):
    parsed = urlparse(url)
    encoded_path = quote(parsed.path)
    return urlunparse((parsed.scheme, parsed.netloc, encoded_path, parsed.params, parsed.query, parsed.fragment))

# 🔍 Check if image is broken
def check_image(image_url, source_page):
    if "email-protection" in image_url.lower() or image_url in checked_image_urls:
        return

    checked_image_urls.add(image_url)

    try:
        encoded_url = sanitize_url(image_url)
        domain = f"{urlparse(source_page).scheme}://{urlparse(source_page).netloc}"

        # log(f"\n[Website]: {domain}")
        # log(f"[Page]: {source_page}")
        # log(f"[Line with Issue]:")
         # If URL is CDN, perform a deeper check (e.g., Cloudflare, Akamai, AWS S3)
        if "cdn" in image_url.lower() or "cloudflare" in image_url.lower() or "akamai" in image_url.lower():
            log(f" - CDN Image Detected: {encoded_url}")

        if '%' in encoded_url:
            log(f"\n[Website]: {domain}")
            log(f"[Page]: {source_page}")
            log(f"[Line with Issue]:")
            log(f" - Encoded URL Detected: {encoded_url}")

        response = requests.head(image_url, timeout=5)
        if response.status_code >= 400:
            log(f"\n[Website]: {domain}")
            log(f"[Page]: {source_page}")
            log(f"[Line with Issue]:")
            log(f" - Broken Image: {image_url} --> {response.status_code}")

    except Exception as e:
        log(f" - Broken Image: {image_url} (Exception: {e})")

# Crawl and scan a single page
def crawl_page(url, base_domain):
    if url in visited_pages:
        return []

    visited_pages.add(url)
    print(f"🌐 Crawling: {url}")

    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            log(f"[Failed to load]: {url}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')

        # ✅ Check images in <img> tags
        for img in soup.find_all('img', src=True):
            full_url = urljoin(url, img['src'])
            check_image(full_url, url)

        # ✅ Check images in <picture> tags
        for picture in soup.find_all('picture'):
            for source in picture.find_all('source', srcset=True):  
                full_url = urljoin(url, source['srcset'])
                check_image(full_url, url) 
            img = picture.find('img', src=True)
            if img:
                full_url = urljoin(url, img['src'])
                check_image(full_url, url)

        # Return internal links to crawl more
        internal_links = set()
        for a in soup.find_all('a', href=True):
            href = a['href']
            full_link = urljoin(url, href)
            parsed = urlparse(full_link)
            if parsed.netloc == base_domain and "#" not in full_link:
                internal_links.add(full_link)

        return list(internal_links)

    except Exception as e:
        log(f"[Error crawling]: {url} ({e})")
        return []

# Crawl entire website recursively
def crawl_website(start_url):
    global visited_pages, checked_image_urls
    visited_pages = set()
    checked_image_urls = set()
    set_output_file(start_url)

    base_domain = urlparse(start_url).netloc
    to_visit = [start_url]

    while to_visit:
        current = to_visit.pop()
        new_links = crawl_page(current, base_domain)
        to_visit.extend([link for link in new_links if link not in visited_pages])

    print(f"✅ Done crawling {start_url}\n")

# ▶️ START HERE
if __name__ == "__main__":
    websites = [
    "https://azerbaijan-e-visas.com"
    # "https://bahrain-evisa.com",
    # "https://egypt-evisa.net/",
    # "https://evisa-to-kenya.org/",
    # "https://india-e-visa.info/"
    ]

    for site in websites:
        crawl_website(site)
