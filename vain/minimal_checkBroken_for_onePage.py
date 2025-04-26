import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse, quote
import string

# Encode non-ASCII or special characters in image URL
def sanitize_url(url):
    parsed = urlparse(url)
    encoded_path = quote(parsed.path)
    return urlunparse((parsed.scheme, parsed.netloc, encoded_path, parsed.params, parsed.query, parsed.fragment))

# Check and print image issues
def check_image(image_url, source_page):
    try:
        encoded_url = sanitize_url(image_url)

        if '%' in encoded_url:
            print(f"##### there is some issue in URL --> web page URL --> {source_page} --> URL of the image --> {encoded_url}")

        response = requests.head(encoded_url, timeout=5)
        if response.status_code >= 400:
            print(f"#### not found URL --> web page URL --> {source_page} --> URL of the image --> {encoded_url}")
    except Exception as e:
        print(f"#### not found URL --> web page URL --> {source_page} --> URL of the image --> {image_url} (Exception: {e})")

# Analyze anchor tags and check for spacing/punctuation issues
def check_anchor_issues(soup, page_url):
    anchors = soup.find_all('a', href=True)
    for anchor in anchors:
        try:
            parent = anchor.find_parent()
            if parent is None:
                continue

            full_html = str(parent)
            anchor_html = str(anchor)

            if anchor_html not in full_html:
                continue

            parts = full_html.split(anchor_html)
            if len(parts) != 2:
                continue

            before, after = parts
            last_char_before = before[-1] if before else ''
            first_char_after = after[0] if after else ''

            # Updated logic: skip warning if clean block context
            missing_space_before = (
                last_char_before and
                not last_char_before.isspace() and
                last_char_before != '>'
            )
            missing_space_after = (
                first_char_after and
                not first_char_after.isspace() and
                first_char_after not in string.punctuation and
                first_char_after != '<'
            )

            anchor_text = anchor.get_text(strip=True)
            ends_with_punctuation = anchor_text and anchor_text[-1] in string.punctuation

            if missing_space_before or missing_space_after or ends_with_punctuation:
                print(f"\n[Website]: {urlparse(page_url).scheme}://{urlparse(page_url).netloc}")
                print(f"[Page]: {page_url}")
                print("[Line with Issue]:")
                print(full_html.strip())

                if missing_space_before:
                    print("[⚠️ Warning] No space before <a> tag")
                if missing_space_after:
                    print("[⚠️ Warning] No space after </a> tag")
                if ends_with_punctuation:
                    print(f"[⚠️ Warning] Anchor text ends with punctuation: '{anchor_text[-1]}'")

        except Exception as e:
            print(f"[Error processing anchor on {page_url}]: {e}")

# Process a single web page
def check_page(page_url):
    try:
        response = requests.get(page_url, timeout=5)
        if response.status_code != 200:
            print(f"[Error] Could not load page: {page_url}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. Image check
        images = soup.find_all('img', src=True)
        for img in images:
            full_img_url = urljoin(page_url, img['src'])
            check_image(full_img_url, page_url)

        # 2. Anchor tag check (in any tag)
        check_anchor_issues(soup, page_url)

    except Exception as e:
        print(f"[Error fetching page] {page_url}: {e}")

# Example usage
if __name__ == "__main__":
    check_page("https://online.djibouti-evisa.com/djibouti-visa-types/")
