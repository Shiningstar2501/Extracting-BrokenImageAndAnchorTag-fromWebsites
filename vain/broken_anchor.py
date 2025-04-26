import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse, quote
import string
import os

visited_pages = set()
checked_image_urls = set()
output_file = None
all_anchor_issues = set()

# Create output directory
output_folder = "output_files"
os.makedirs(output_folder, exist_ok=True)

# Set file name based on domain
def set_output_file(start_url):
    global output_file
    domain = urlparse(start_url).netloc.replace(".", "-")
    output_file = os.path.join(output_folder, f"{domain}-output.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"[Scanning] {start_url}\n")

# Print + write to file
def log(message):
    print(message)
    with open(output_file, "a", encoding="utf-8") as f:
        f.write(message + "\n")

# Encode unsafe URLs
def sanitize_url(url):
    parsed = urlparse(url)
    encoded_path = quote(parsed.path)
    return urlunparse((parsed.scheme, parsed.netloc, encoded_path, parsed.params, parsed.query, parsed.fragment))

# Check an image URL
def check_image(image_url, source_page):
    if "email-protection" in image_url.lower():
        return

    if image_url in checked_image_urls:
        return

    checked_image_urls.add(image_url)

    try:
        encoded_url = sanitize_url(image_url)
        domain = f"{urlparse(source_page).scheme}://{urlparse(source_page).netloc}"
        issue_detected = False
        log(f"\n[Website]: {domain}")
        log(f"[Page]: {source_page}")
        if '%' in encoded_url:
         
            log(f"[Line with Issue]:")
            log(f" - Encoded URL Detected: {encoded_url}")
            issue_detected = True

        response = requests.head(encoded_url, timeout=5)
        if response.status_code >= 400:
            if not issue_detected:
                # log(f"\n[Website]: {domain}")
                # log(f"[Page]: {source_page}")
                log(f"[Line with Issue]:")
            log(f" - Broken Image: {encoded_url} --> {response.status_code}")

    except Exception as e:
        # log(f"\n[Website]: {urlparse(source_page).scheme}://{urlparse(source_page).netloc}")
        # log(f"[Page]: {source_page}")
        log(f"[Line with Issue]:")
        log(f" - Broken Image: {image_url} (Exception: {e})")


# def check_anchor_issues(soup, page_url):
#     anchors = soup.find_all('a', href=True)

#     for anchor in anchors:
#         try:
#             href = anchor['href']
#             if "#" in href or "www.dmca.com" in href or "email-protection" in href.lower():
#                 continue

#             anchor_html = str(anchor).strip()
#             anchor_text = anchor.get_text()

#             whitespace_inside_start = anchor_text and anchor_text[0].isspace()
#             whitespace_inside_end = anchor_text and anchor_text[-1].isspace()
#             ends_with_punctuation = anchor_text.strip() and anchor_text.strip()[-1] in string.punctuation

#             parent_html = str(anchor.find_parent())
#             if anchor_html not in parent_html:
#                 continue

#             parts = parent_html.split(anchor_html)
#             if len(parts) != 2:
#                 continue

#             before, after = parts
#             last_char_before = before[-1] if before else ''
#             first_char_after = after[0] if after else ''

#             if last_char_before:
#                 space_before_anchor = last_char_before.isspace() or last_char_before == '>'
#             else:
#                 space_before_anchor = False

#             if first_char_after:
#                 space_after_anchor = first_char_after.isspace() or first_char_after == '<'
#             else:
#                 space_after_anchor = False

#             has_icon_child = anchor.find(["span", "i"], class_=lambda c: c and ("flag" in c.split() or "fa" in c.split()))

#             issue_messages = []

#             if whitespace_inside_start:
#                 issue_messages.append("[⚠️] Unwanted space immediately after opening <a> tag")
#             if whitespace_inside_end:
#                 issue_messages.append("[⚠️] Unwanted space immediately before closing </a> tag")
#             if not space_after_anchor:
#                 issue_messages.append("[⚠️] No space or tag immediately after </a> tag")
#             if not space_before_anchor:
#                 issue_messages.append("[⚠️] No space or tag immediately before <a> tag")
#             if ends_with_punctuation:
#                 issue_messages.append(f"[⚠️] Anchor text ends with punctuation: '{anchor_text.strip()[-1]}'")

#             if has_icon_child:
#                 issue_messages = [msg for msg in issue_messages if "after opening" not in msg and "after </a>" not in msg]

#             if issue_messages:
#                 issue_key = (anchor_html, tuple(issue_messages))
#                 all_anchor_issues.add(issue_key)

#         except Exception as e:
#             log(f"[Error processing anchor on {page_url}]: {e}")
            
def check_anchor_issues(soup, page_url):
    anchors = soup.find_all('a', href=True)

    for anchor in anchors:
        try:
            href = anchor['href']
            if "#" in href or "www.dmca.com" in href or "email-protection" in href.lower():
                continue

            anchor_html = str(anchor).strip()
            anchor_text = anchor.get_text()

            # Inside <a>: whitespace checks
            whitespace_inside_start = anchor_text and anchor_text[0].isspace()
            whitespace_inside_end = anchor_text and anchor_text[-1].isspace()

            # Inside <a>: punctuation check
            ends_with_punctuation = anchor_text.strip() and anchor_text.strip()[-1] in string.punctuation

            # Outside <a>: check space before/after in parent HTML
            parent_html = str(anchor.find_parent())
            if anchor_html not in parent_html:
                continue

            parts = parent_html.split(anchor_html)
            if len(parts) != 2:
                continue

            before, after = parts
            last_char_before = before[-1] if before else ''
            first_char_after = after[0] if after else ''

            space_before_anchor = last_char_before.isspace() or last_char_before == '>'
            space_after_anchor = first_char_after.isspace() or first_char_after == '<'

            # Exception: allow space if icon child (flag/fa class)
            has_icon_child = anchor.find(["span", "i"], class_=lambda c: c and ("flag" in c.split() or "fa" in c.split()))

            issue_messages = []

            if whitespace_inside_start:
                issue_messages.append("[⚠️] Unwanted space immediately after opening <a> tag")
            if whitespace_inside_end:
                issue_messages.append("[⚠️] Unwanted space immediately before closing </a> tag")
            if not space_after_anchor:
                issue_messages.append("[⚠️] No space or tag immediately after </a> tag")
            if not space_before_anchor:
                issue_messages.append("[⚠️] No space or tag immediately before <a> tag")
            if ends_with_punctuation:
                issue_messages.append(f"[⚠️] Anchor text ends with punctuation: '{anchor_text.strip()[-1]}'")

            # Remove specific errors if it's a flag/fa icon child
            if has_icon_child:
                issue_messages = [msg for msg in issue_messages if "after opening" not in msg and "after </a>" not in msg]

            # Store the issues in the dictionary, grouped by page
            if issue_messages:
                if page_url not in all_anchor_issues:
                    all_anchor_issues[page_url] = set()
                all_anchor_issues[page_url].add((anchor_html, tuple(issue_messages)))

        except Exception as e:
            log(f"[Error processing anchor on {page_url}]: {e}")

def print_all_anchor_issues(domain_url):
    if all_anchor_issues:
        log(f"\n[Unique Anchor Issues for Website]: {domain_url}")
        for page_url, issues in all_anchor_issues.items():
            log(f"\n[Page]: {page_url}")
            for anchor_html, messages in issues:
                log("[Line with Issue]:")
                log(anchor_html)
                for msg in messages:
                    log(msg)



# def check_anchor_issues(soup, page_url):
    # from urllib.parse import urlparse

    # anchors = soup.find_all('a', href=True)
    # issues_found = []

    # for anchor in anchors:
    #     try:
    #         href = anchor['href']
    #         if "#" in href or "www.dmca.com" in href or "email-protection" in href.lower():
    #             continue

    #         anchor_html = str(anchor).strip()
    #         anchor_text = anchor.get_text()

    #         # Check inside <a>: space after <a> and before </a>
    #         whitespace_inside_start = anchor_text and anchor_text[0].isspace()
    #         whitespace_inside_end = anchor_text and anchor_text[-1].isspace()

    #         # Check punctuation before </a>
    #         ends_with_punctuation = anchor_text.strip() and anchor_text.strip()[-1] in string.punctuation

    #         # Check outside <a>: space before <a> and after </a>
    #         parent_html = str(anchor.find_parent())
    #         if anchor_html not in parent_html:
    #             continue

    #         parts = parent_html.split(anchor_html)
    #         if len(parts) != 2:
    #             continue

    #         before, after = parts
    #         last_char_before = before[-1] if before else ''
    #         first_char_after = after[0] if after else ''

    #         # Check space before <a>
    #         if last_char_before:
    #             if last_char_before == '>':
    #                 space_before_anchor = True  # Tag before <a> is allowed
    #             else:
    #                 space_before_anchor = last_char_before.isspace()
    #         else:
    #             space_before_anchor = False

    #         # Check space after </a>
    #         if first_char_after:
    #             if first_char_after == '<':
    #                 space_after_anchor = True  # Another tag after </a> is allowed
    #             else:
    #                 space_after_anchor = first_char_after.isspace()
    #         else:
    #             space_after_anchor = False

    #         # Check for exceptions: if anchor has flag/fa icon, allow space after it
    #         has_icon_child = anchor.find(["span", "i"], class_=lambda c: c and ("flag" in c.split() or "fa" in c.split()))

    #         issue_messages = []

    #         # Condition 1: No space after <a>
    #         if whitespace_inside_start:
    #             issue_messages.append("[⚠️] Unwanted space immediately after opening <a> tag")

    #         # Condition 2: No space before </a>
    #         if whitespace_inside_end:
    #             issue_messages.append("[⚠️] Unwanted space immediately before closing </a> tag")

    #         # Condition 3: There MUST be space after </a> unless it's a closing tag
    #         if not space_after_anchor:
    #             issue_messages.append("[⚠️] No space or tag immediately after </a> tag")

    #         # Condition 4: There MUST be space before <a> unless it's an opening tag
    #         if not space_before_anchor:
    #             issue_messages.append("[⚠️] No space or tag immediately before <a> tag")

    #         # Condition 7: No punctuation before </a>
    #         if ends_with_punctuation:
    #             issue_messages.append(f"[⚠️] Anchor text ends with punctuation: '{anchor_text.strip()[-1]}'")

    #         # Condition 8: Allow space after icon (flag/fa)
    #         if has_icon_child:
    #             if "[⚠️] Unwanted space immediately after opening <a> tag" in issue_messages:
    #                 issue_messages.remove("[⚠️] Unwanted space immediately after opening <a> tag")
    #             if "[⚠️] No space or tag immediately after </a> tag" in issue_messages:
    #                 issue_messages.remove("[⚠️] No space or tag immediately after </a> tag")

    #         if issue_messages:
    #             issues_found.append((anchor_html, issue_messages))

    #     except Exception as e:
    #         log(f"[Error processing anchor on {page_url}]: {e}")

    # # Grouped logging only once per page (if there are issues)
    # if issues_found:
    #     log(f"\n[Website]: {urlparse(page_url).scheme}://{urlparse(page_url).netloc}")
    #     log(f"[Page]: {page_url}")
    #     for anchor_html, messages in issues_found:
    #         log("[Line with Issue]:")
    #         log(anchor_html)
    #         for msg in messages:
    #             log(msg)

# Process a single page
def crawl_page(url, base_domain):
    if "community" in url.lower() or "email-protection"  in url.lower() or "blogs" in url.lower():
        log(f"[Skipping disallowed page] {url}")
        return []

    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            log(f"[Error] Could not load page: {url}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')

        # <img>
        images = soup.find_all('img', src=True)
        for img in images:
            full_img_url = urljoin(url, img['src'])
            check_image(full_img_url, url)

        # <picture>
        pictures = soup.find_all('picture')
        for picture in pictures:
            sources = picture.find_all('source', srcset=True)
            for src in sources:
                full_src_url = urljoin(url, src['srcset'])
                check_image(full_src_url, url)
            img = picture.find('img', src=True)
            if img:
                full_img_url = urljoin(url, img['src'])
                check_image(full_img_url, url)

        # Anchors
        check_anchor_issues(soup, url)

        # Internal links
        links = soup.find_all('a', href=True)
        page_links = [
            urljoin(url, a['href']) for a in links
            if urlparse(urljoin(url, a['href'])).netloc == base_domain
        ]
        # Filter links with disallowed patterns
        page_links = [
            link for link in page_links
            if "community" not in link.lower() and "email-protection" not in link.lower()
        ]
        return page_links

    except Exception as e:
        log(f"[Error crawling page {url}]: {e}")
        return []

# Crawl entire website
def crawl_website(start_url):
    global visited_pages, checked_image_urls, all_anchor_issues
    visited_pages = set()
    checked_image_urls = set()
    all_anchor_issues = {}
    set_output_file(start_url)

    domain = urlparse(start_url).netloc
    to_visit = [start_url]

    while to_visit:
        url = to_visit.pop()
        if url in visited_pages:
            continue
        visited_pages.add(url)
        log(f"\n[Crawling] {url}")
        links = crawl_page(url, domain)
        to_visit.extend([link for link in links if link not in visited_pages])

    # ✅ At the end: print unique issues once per domain
    print_all_anchor_issues(start_url)

# Run it
if __name__ == "__main__":
    urls = [
    # "https://albania-evisa.org/",
    "https://benin-e-visa.com/",
    "https://bolivia-evisa.com/",
    "https://bosnia-evisa.com/",
    "https://botswana-visa.com/",
    "https://bulgaria-evisa.com/",
    "https://cameroon-evisa.com/",
    "https://chile-evisa.com/",
    "https://congo-evisa.com/",
    "https://online.djibouti-evisa.com/",
    "https://e-visa-cambodia.com/",
    "https://online.e-visa-southafrica.com/",
    "https://egypt-eta.com/",
    "https://eta-canada.info/",
    "https://eta-cuba.com/",
    "https://ethiopia-e-visa.com/",
    "https://online.evisa-madagascar.com/",
    "https://evisa-moldova.com/",
    "https://evisa-myanmar.com/",
    "https://evisa-to-saudi-arabia.com/",
    "https://georgia-e-visa.com/",
    "https://india-s-travel.com/",
    "https://indonesia-e-visa.com/",
    "https://japanevisa.net/",
    "https://lao-evisa.com/",
    "https://libya-e-visa.com/",
    "https://malaysia-e-visa.com/",
    "https://mexico-e-visa.com/",
    "https://morocco-e-visas.com/",
    "https://nigeria-e-visa.com/",
    "https://nz-eta.info/",
    "https://romania-e-visa.com/",
    "https://russian-e-visa.com/",
    "https://south-korea-evisa.com/",
    "https://online.tanzania-e-visas.com/",
    "https://thailand-e-visas.com/",
    "https://tunisia-e-visa.com/",
    "https://turkey-evisa.it.com/",
    "https://united-kingdom-visa.com/",
    "https://vietnam-e-visas.com/",
    "https://visa-armenia.com/",
    "https://visa-kuwait.com/",
    "https://visa-qatar.com/",
    # "https://zambia-visa.com/",
    # "https://zimbabwe-visa.com/"
]

    for site in urls:
        crawl_website(site)
