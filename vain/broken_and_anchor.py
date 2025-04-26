import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor
import os

visited_pages = set()
OUTPUT_FILE = "brokenandanchor.txt"

# Reset output file
if os.path.exists(OUTPUT_FILE):
    os.remove(OUTPUT_FILE)

def log_to_output(content):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(content + "\n")

def get_all_links_from_page(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return [], [], ""
        
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')

        # Collect image links
        image_links = []
        for img in soup.find_all('img', src=True):
            src = img['src'].strip()
            if src:
                image_links.append(urljoin(url, src))

        # Collect internal page links
        page_links = []
        domain = urlparse(url).netloc
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href'].strip()
            if href:
                full_url = urljoin(url, href)
                if urlparse(full_url).netloc == domain:
                    page_links.append(full_url)

        return list(set(image_links)), list(set(page_links)), html_content
    except Exception as e:
        print(f"[Error fetching page] {url}: {e}")
        return [], [], ""

def check_paragraph_anchor_spacing(page_url, html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    problem_count = 0

    for p in soup.find_all('p'):
        p_html = str(p)
        anchors = p.find_all('a')

        for a in anchors:
            anchor_html = str(a)
            idx = p_html.find(anchor_html)

            if idx != -1:
                before = p_html[idx - 1] if idx > 0 else ''
                after = p_html[idx + len(anchor_html)] if idx + len(anchor_html) < len(p_html) else ''

                if before not in [' ', '\n', '\t'] or after not in [' ', '.', ',', ';', '!', '?', '\n', '\t']:
                    log_to_output(f"[{page_url}] Spacing issue in <p>: ...{p_html.strip()[:200]}...")
                    problem_count += 1

    if problem_count:
        log_to_output(f"Total anchor spacing issues found on this page: {problem_count}")

def crawl_website(start_url):
    to_visit = [start_url]
    all_image_links = []

    while to_visit:
        url = to_visit.pop()
        if url in visited_pages:
            continue
        visited_pages.add(url)
        print(f"[Crawling] {url}")
        images, links, html = get_all_links_from_page(url)
        all_image_links.extend(images)

        if html:
            check_paragraph_anchor_spacing(url, html)

        to_visit.extend([link for link in links if link not in visited_pages])

    return list(set(all_image_links))

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
        global visited_pages
        visited_pages = set()

        log_to_output(f"\n\n==============================\nScanning: {site}\n==============================")
        
        image_urls = crawl_website(site)
        log_to_output(f"\n[Total Images Found] {len(image_urls)}")

        broken_images = check_broken_images(image_urls)
        log_to_output(f"[Broken Images Found] {len(broken_images)}")
        for url, error in broken_images:
            log_to_output(f" - {url} --> {error}")

        log_to_output("***************************************")

    print("\n[Scan Complete] Check 'brokenandanchor.txt' for results.")
    if os.path.exists(OUTPUT_FILE):
        print(f"Results saved to: {OUTPUT_FILE}")
    else:
        print("No output generated.")

if __name__ == "__main__":
    websites = [
        "https://morocco-e-visas.com/morocco-evisa-for-georgia/"
        # Add more websites if needed
    ]
    main(websites)
