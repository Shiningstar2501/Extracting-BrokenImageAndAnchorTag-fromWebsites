import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import string
import os
import re

all_anchor_issues = {}

# ✅ Utility: Extract domain from a URL
def get_base_domain(url):
    return urlparse(url).netloc

# ✅ Phase 1: Check if the link is internal
def is_internal_link(href, base_domain):
    parsed = urlparse(href)
    return parsed.netloc == "" or parsed.netloc == base_domain

# ✅ Phase 1: Clean links (remove fragments and junk)
def clean_and_filter(href, base_url):
    full_url = urljoin(base_url, href)
    if "#" in full_url or "email-protection" in full_url:
        return None
    return full_url.split("#")[0]  # Remove any anchor fragments

# ✅ Phase 1: Collect internal links from a soup object
def extract_internal_links(soup, base_url, base_domain):
    links = set()
    for a in soup.find_all("a", href=True):
        href = a['href']
        if is_internal_link(href, base_domain):
            cleaned = clean_and_filter(href, base_url)
            if cleaned:
                links.add(cleaned)
    return links

# ✅ Phase 2: Download and filter page content
def get_page_content(page_url, home_url):
    try:
        response = requests.get(page_url, timeout=10)
        if response.status_code != 200:
            print(f"❌ Could not load page: {page_url}")
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # Use full content for homepage
        if page_url == home_url:
            return soup

        # For sub-pages: remove layout elements
        for tag in ['header', 'footer', 'nav']:
            for section in soup.find_all(tag):
                section.decompose()

        # Use <main> content if it exists
        # main = soup.find('main')
        # if main:
        #     return BeautifulSoup(str(main), 'html.parser')

        return soup  # fallback: return cleaned soup

    except Exception as e:
        print(f"🚨 Error fetching page {page_url}: {e}")
        return None

# 🧪 Placeholder for anchor issue checker (Phase 3)
def check_anchor_issues(soup, page_url):
    print(f"🔍 Checking anchors on: {page_url}")
    # (We'll implement this in Phase 3)

# ✅ Main crawler combining phase 1 and 2
def crawl_website(home_url):
    base_domain = get_base_domain(home_url)
    pages_to_crawl = set([home_url])
    visited_pages = set()

    while pages_to_crawl:
        page_url = pages_to_crawl.pop()
        if page_url in visited_pages:
            continue

        print(f"🌐 Crawling page: {page_url}")
        visited_pages.add(page_url)

        # Get and filter page content
        content = get_page_content(page_url, home_url)
        if content:
            # Step 1: Check anchor issues (to be fully built in Phase 3)
            if not is_excluded_page(page_url):
                check_anchor_issues(content, page_url)

            # Step 2: Extract more internal links from this page
            new_links = extract_internal_links(content, page_url, base_domain)
            pages_to_crawl.update(new_links - visited_pages)

    print(f"✅ Done. Crawled {len(visited_pages)} unique page(s).")

def is_excluded_page(url):
    lowered = url.lower()
    return "/blog" in lowered or "/community" in lowered or "/web-sitemap" in lowered


def check_anchor_issues(soup, page_url):
    anchors = soup.find_all('a', href=True)

    for anchor in anchors:
        try:
            href = anchor['href']
            if "#" in href or "dmca.com" in href or "email-protection" in href.lower():
                continue

            anchor_html = str(anchor).strip()
            anchor_text = anchor.get_text()

            # Inside anchor text
            whitespace_inside_start = anchor_text and anchor_text[0].isspace()
            whitespace_inside_end = anchor_text and anchor_text[-1].isspace()
            ends_with_punctuation = anchor_text.strip() and anchor_text.strip()[-1] in string.punctuation

            # Check surrounding context
            parent_html = str(anchor.find_parent())
            if anchor_html not in parent_html:
                continue

            before, after = parent_html.split(anchor_html, 1)
            last_char_before = before[-1] if before else ''
            first_char_after = after[0] if after else ''

            space_before_anchor = last_char_before.isspace() or last_char_before == '>'   or  first_char_after == '"'
            space_after_anchor = first_char_after.isspace() or first_char_after == '<' or  first_char_after == '.' or  first_char_after == ','  or  first_char_after == '"'

            has_icon_child = anchor.find(["span", "i"], class_=lambda c: c and ("flag" in c.split() or "fa" in c.split()))

            issue_messages = []

            if whitespace_inside_start:
                issue_messages.append("[⚠️] Unwanted space immediately after opening <a> tag")
            if whitespace_inside_end:
                issue_messages.append("[⚠️] Unwanted space immediately before closing </a> tag")
            if not space_before_anchor:
                issue_messages.append("[⚠️] No space or tag immediately before <a> tag")
            if not space_after_anchor:
                issue_messages.append("[⚠️] No space or tag immediately after </a> tag")
            if ends_with_punctuation:
                issue_messages.append(f"[⚠️] Anchor text ends with punctuation: '{anchor_text.strip()[-1]}'")

            if has_icon_child:
                issue_messages = [
                    msg for msg in issue_messages
                    if "after opening" not in msg and "after </a>" not in msg
                ]

            if issue_messages:
                key = (anchor_html, tuple(issue_messages))
                if key not in all_anchor_issues:
                    all_anchor_issues[key] = set()
                all_anchor_issues[key].add(page_url)

        except Exception as e:
            print(f"Error processing anchor on {page_url}: {e}")

def sanitize_filename(url):
    # Remove http/https and replace unsafe filename characters
    cleaned = re.sub(r"https?://", "", url)
    cleaned = re.sub(r"[^\w.-]", "_", cleaned)
    return cleaned

def print_anchor_issues_for_all(domains):
    output_folder = "OutputFiles"
    
    # Create output folder only if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for domain_url in domains:
        domain_name = sanitize_filename(domain_url)
        file_path = os.path.join(output_folder, f"{domain_name}_anchor_issues.txt")

        with open(file_path, 'w', encoding='utf-8') as f:
            if all_anchor_issues:
                f.write(f"[Unique Anchor Issues for Website]: {domain_url}\n\n")
                for (anchor_html, messages), pages in all_anchor_issues.items():
                    f.write("[Line with Issue]:\n")
                    f.write(anchor_html + "\n")
                    for msg in messages:
                        f.write(msg + "\n")
                    f.write("[Pages this occurred on]:\n")
                    for page in sorted(pages):
                        f.write(f" - {page}\n")
                    f.write("\n")
            else:
                f.write("No anchor issues found.\n")

        print(f"📁 Anchor issues saved to: {file_path}")

# ▶️ Run it
if __name__ == "__main__":
    websites = [
    "https://albania-evisa.org/",
    "https://bolivia-evisa.com/",
    "https://bosnia-evisa.com/",
    "https://botswana-visa.com/",
    "https://bulgaria-evisa.com/",
    "https://cameroon-evisa.com/",
    "https://e-visa-cambodia.com/",
    "https://egypt-eta.com/",
    "https://eta-canada.info/",
    "https://eta-cuba.com/",
    "https://ethiopia-e-visa.com/",
    "https://georgia-e-visa.com/",
    "https://lao-evisa.com/",
    "https://malaysia-e-visa.com/",
    "https://nigeria-e-visa.com/",
    "https://romania-e-visa.com/",
    "https://online.tanzania-e-visas.com/",
    "https://thailand-e-visas.com/",
    "https://visa-qatar.com/",  
    "https://united-kingdom-visa.com/",
    "https://vietnam-e-visas.com/",
    "https://zimbabwe-visa.com/"
]

    
    for site in websites:
        all_anchor_issues.clear()  # Clear previous site's issues before crawling the next one
        crawl_website(site)
        print_anchor_issues_for_all([site])

