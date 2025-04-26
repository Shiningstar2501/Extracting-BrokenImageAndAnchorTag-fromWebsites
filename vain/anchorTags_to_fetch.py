import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import string

visited_pages = set()
OUTPUT_FILE = "anchor_blocks.txt"

if os.path.exists(OUTPUT_FILE):
    os.remove(OUTPUT_FILE)

def log_to_output(content):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(content + "\n")

def get_anchors_from_page(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        anchors = soup.find_all('a', href=True)
        website = f"{urlparse(url).scheme}://{urlparse(url).netloc}"

        for anchor in anchors:
            try:
                parent = anchor.find_parent()
                if parent is None or parent.name != "p":
                    continue  # ✅ Only <a> inside <p> tags

                full_html = str(parent)
                anchor_html = str(anchor)

                if anchor_html not in full_html:
                    continue  # Skip malformed

                parts = full_html.split(anchor_html)
                if len(parts) != 2:
                    continue

                before, after = parts
                last_char_before = before[-1] if before else ''
                first_char_after = after[0] if after else ''

                # 1. Check for missing space around <a>
                missing_space_before = last_char_before and not last_char_before.isspace()
                missing_space_after = (
                    first_char_after and
                    not first_char_after.isspace() and
                    first_char_after not in string.punctuation
                )

                # 2. Check anchor text ends with punctuation
                anchor_text = anchor.get_text(strip=True)
                ends_with_punctuation = anchor_text and anchor_text[-1] in string.punctuation

                if missing_space_before or missing_space_after or ends_with_punctuation:
                    log_to_output(f"\n[Website]: {website}")
                    log_to_output(f"[Page]: {url}")
                    log_to_output("[Line with Issue]:")
                    log_to_output(full_html.strip())

                    if missing_space_before:
                        log_to_output("[⚠️ Warning] No space before <a> tag")
                    if missing_space_after:
                        log_to_output("[⚠️ Warning] No space after </a> tag")
                    if ends_with_punctuation:
                        log_to_output(f"[⚠️ Warning] Anchor text ends with punctuation: '{anchor_text[-1]}'")

            except Exception as e:
                log_to_output(f"Error processing anchor on {url}: {e}")

        # Return valid same-domain links for further crawling
        domain = urlparse(url).netloc
        page_links = [urljoin(url, a['href']) for a in anchors]
        page_links = [link for link in page_links if urlparse(link).netloc == domain]
        return page_links

    except Exception as e:
        log_to_output(f"[Error fetching page] {url}: {e}")
        return []

def crawl_website(start_url):
    to_visit = [start_url]
    while to_visit:
        url = to_visit.pop()
        if url in visited_pages:
            continue
        visited_pages.add(url)
        print(f"[Crawling] {url}")
        links = get_anchors_from_page(url)
        to_visit.extend([link for link in links if link not in visited_pages])

def main(websites):
    for site in websites:
        log_to_output(f"\n==============================")
        log_to_output(f"[Scanning Website] {site}")
        log_to_output(f"==============================")
        global visited_pages
        visited_pages = set()
        crawl_website(site)

    print("\n[Done] Check 'anchor_blocks.txt' for results.")

if __name__ == "__main__":
   websites = [
    # "http://albania-evisa.org/",
    # "http://azerbaijan-e-visa.com/",
    # "http://bahrain-evisa.com/",
    # "http://benin-e-visa.com/",
    # "http://bolivia-evisa.com/",
    # "http://bosnia-evisa.com/",
    # "http://botswana-visa.com/",
    # "http://bulgaria-evisa.com/",
    # "http://cameroon-evisa.com/",
    # "http://chile-evisa.com/",
    # "http://congo-evisa.com/",
    # "http://djibouti-evisa.com/",
    # "http://e-visa-cambodia.com/",
    # "http://e-visa-southafrica.com/",
    # "http://egypt-e-visa.org/",
    # "http://egypt-eta.com/",
    # "http://eta-canada.info/",
    # "http://eta-cuba.com/",
    # "http://ethiopia-e-visa.com/",
    # "http://evisa-madagascar.com/",
    # "http://evisa-moldova.com/",
    # "http://evisa-myanmar.com/",
    # "http://evisa-to-kenya.org/",
    # "http://evisa-to-saudi-arabia.com/",
    # "http://georgia-e-visa.com/",
    # "http://india-e-visa.net/",
    # "http://india-s-travel.com/",
    # "http://indonesia-e-visa.com/",
    # "http://japanevisa.net/",
    # "http://lao-evisa.com/",
    # "http://libya-e-visa.com/",
    # "http://malaysia-e-visa.com/",
    # "http://mexico-e-visa.com/",
    # "http://morocco-e-visas.com/",
    # "http://nigeria-e-visa.com/",
    # "http://nz-eta.info/",
    # "http://philippines-evisa.org/",
    # "http://romania-e-visa.com/",
    # "http://russian-e-visa.com/",
    # "http://south-korea-evisa.com/",
    # "http://tanzania-e-visas.com/",
    # "http://thailand-e-visas.com/",
    # "http://tunisia-e-visa.com/",
    # "http://turkey-e-visas.com/",
    # "http://united-kingdom-visa.com/",
    # "http://vietnam-e-visas.com/",
    # "http://visa-armenia.com/",
    # "http://visa-kuwait.com/",
    # "http://visa-qatar.com/",
    # "http://zambia-visa.com/",
    # "http://zimbabwe-visa.com/"
    "https://online.djibouti-evisa.com/djibouti-visa-types/"
    ]
   main(websites)
