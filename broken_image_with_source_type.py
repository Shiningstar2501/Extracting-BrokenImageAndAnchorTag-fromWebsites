
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse, quote, unquote
import os

# Global stores
visited_pages = set()
checked_image_urls = set()
output_file = None

# Create output directory
output_folder = "BrokenImageReports"
os.makedirs(output_folder, exist_ok=True)

def set_output_file(start_url):
    global output_file
    domain = urlparse(start_url).netloc.replace(".", "-")
    output_file = os.path.join(output_folder, f"{domain}-broken-images.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"[Scanning Images for] {start_url}")

def log(message):
    print(message)
    with open(output_file, "a", encoding="utf-8") as f:
        f.write(message + "\n")

def sanitize_url(url):
    parsed = urlparse(url)
    decoded_path = unquote(parsed.path)
    encoded_path = quote(decoded_path, safe="/")
    return urlunparse((parsed.scheme, parsed.netloc, encoded_path, parsed.params, parsed.query, parsed.fragment))

def contains_non_ascii_or_space(text):
    return any(ord(char) > 127 or char == ' ' for char in text)

def check_image(image_url, source_page, source_type="img"):
    if "email-protection" in image_url.lower() or image_url in checked_image_urls:
        return

    checked_image_urls.add(image_url)

    try:
        encoded_url = sanitize_url(image_url)
        domain = f"{urlparse(source_page).scheme}://{urlparse(source_page).netloc}"

        filename = os.path.basename(urlparse(image_url).path)
        if contains_non_ascii_or_space(filename):
            log(f"\n[Website]: {domain}")
            log(f"[Page]: {source_page}")
            log(f"[Line with Issue]:")
            log(f"[Non-ASCII Image File]: {filename}")

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
            log(f" - Broken Image ({source_type}): {image_url} --> {response.status_code}")

    except Exception as e:
        log(f" - Broken Image ({source_type}): {image_url} (Exception: {e})")

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

        for img in soup.find_all('img', src=True):
            full_url = urljoin(url, img['src'])
            check_image(full_url, url, source_type="img")

        for picture in soup.find_all('picture'):
            img = picture.find('img', src=True)
            if img:
                full_url = urljoin(url, img['src'])
                check_image(full_url, url, source_type="img")

                if not any(cdn in full_url.lower() for cdn in ['cdn', 'cloudflare', 'akamai']):
                    for source in picture.find_all('source', srcset=True):
                        src_url = urljoin(url, source['srcset'])
                        check_image(src_url, url, source_type="source")

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

def crawl_website(start_url):
    global visited_pages, checked_image_urls
    visited_pages = set()
    checked_image_urls = set()
    set_output_file(start_url)

    base_domain = urlparse(start_url).netloc
    crawl_page(start_url, base_domain)
    print(f"✅ Done scanning single page: {start_url}\n")

if __name__ == "__main__":
    websites = [
        "https://azerbaijan-e-visas.com"
    ]

    for site in websites:
        crawl_website(site)
