# # import requests
# # from bs4 import BeautifulSoup
# # from urllib.parse import urljoin, urlparse
# # from concurrent.futures import ThreadPoolExecutor
# # import time

# # visited_pages = set()

# # def get_all_links_from_page(url, image_sources):
# #     try:
# #         response = requests.get(url, timeout=5)
# #         if response.status_code != 200:
# #             return []

# #         soup = BeautifulSoup(response.text, 'html.parser')

# #         # Get all images and store with the page they appear on
# #         images = soup.find_all('img', src=True)
# #         for img in images:
# #             full_img_url = urljoin(url, img['src'])
# #             image_sources[full_img_url] = url

# #         # Get all internal links
# #         domain = urlparse(url).netloc
# #         page_links = [urljoin(url, a['href']) for a in soup.find_all('a', href=True)]
# #         page_links = [link for link in page_links if urlparse(link).netloc == domain]

# #         return page_links
# #     except Exception as e:
# #         print(f"[Error fetching page] {url}: {e}")
# #         return []

# # def crawl_website(start_url):
# #     to_visit = [start_url]
# #     image_sources = {}  # {image_url: source_page}

# #     while to_visit:
# #         url = to_visit.pop()
# #         if url in visited_pages:
# #             continue
# #         visited_pages.add(url)
# #         print(f"[Crawling] {url}")
# #         links = get_all_links_from_page(url, image_sources)
# #         to_visit.extend([link for link in links if link not in visited_pages])

# #     return image_sources

# # def check_image_link(args):
# #     image_url, source_page = args
# #     try:
# #         response = requests.head(image_url, timeout=5)
# #         if response.status_code >= 400:
# #             return source_page, image_url, response.status_code
# #     except Exception as e:
# #         return source_page, image_url, str(e)
# #     return None

# # def check_broken_images(image_sources):
# #     broken = []
# #     print("Checking broken images...")
# #     with ThreadPoolExecutor(max_workers=10) as executor:
# #         results = executor.map(check_image_link, image_sources.items())
# #         for result in results:
# #             if result:
# #                 broken.append(result)
# #     return broken

# # def main(websites):
# #     with open("output_for_broken.txt", "w", encoding="utf-8") as outfile:
# #         for site in websites:
# #             outfile.write(f"\n[Scanning Website] {site}\n")
# #             print(f"\n[Scanning Website] {site}")
# #             global visited_pages
# #             visited_pages = set()

# #             image_sources = crawl_website(site)
# #             outfile.write(f"[Total Images Found] {len(image_sources)}\n")
# #             print(f"[Total Images Found] {len(image_sources)}")

# #             broken_images = check_broken_images(image_sources)
# #             outfile.write(f"[Broken Images Found] {len(broken_images)}\n")
# #             print(f"[Broken Images Found] {len(broken_images)}")

# #             for page, img_url, error in broken_images:
# #                 outfile.write(f"Page: {page}\n")
# #                 outfile.write(f" - Broken Image: {img_url} --> {error}\n\n")
# #                 print(f"Page: {page}")
# #                 print(f" - Broken Image: {img_url} --> {error}")

# #             outfile.write("***************************************\n")
# #             print("***************************************")

# # if __name__ == "__main__":
# #     websites = [
# #     "http://evisa-myanmar.com/",
# #     "http://evisa-to-kenya.org/",
# #     "http://georgia-e-visa.com/",
# #     "http://india-s-travel.com/",
# #     "http://japanevisa.net/",
# #     "http://malaysia-e-visa.com/",
# #     "http://nigeria-e-visa.com/",
# #     "http://vietnam-e-visas.com/"
# #     ]
# #     main(websites)
# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin, urlparse, urlunparse, quote
# from concurrent.futures import ThreadPoolExecutor

# visited_pages = set()

# # Function to encode the path of a URL
# def sanitize_url(url):
#     parsed = urlparse(url)
#     encoded_path = quote(parsed.path)
#     return urlunparse((parsed.scheme, parsed.netloc, encoded_path, parsed.params, parsed.query, parsed.fragment))

# # Get all image links and internal links from a page
# def get_all_links_from_page(url, image_sources):
#     try:
#         response = requests.get(url, timeout=5)
#         if response.status_code != 200:
#             return []

#         soup = BeautifulSoup(response.text, 'html.parser')

#         # Extract images and associate them with the page
#         images = soup.find_all('img', src=True)
#         for img in images:
#             full_img_url = urljoin(url, img['src'])  # Join relative/absolute
#             image_sources[full_img_url] = url

#         # Get all internal links (same domain)
#         domain = urlparse(url).netloc
#         page_links = [urljoin(url, a['href']) for a in soup.find_all('a', href=True)]
#         page_links = [link for link in page_links if urlparse(link).netloc == domain]

#         return page_links
#     except Exception as e:
#         print(f"[Error fetching page] {url}: {e}")
#         return []

# # Crawl entire website starting from a base URL
# def crawl_website(start_url):
#     to_visit = [start_url]
#     image_sources = {}

#     while to_visit:
#         url = to_visit.pop()
#         if url in visited_pages:
#             continue
#         visited_pages.add(url)
#         print(f"[Crawling] {url}")
#         links = get_all_links_from_page(url, image_sources)
#         to_visit.extend([link for link in links if link not in visited_pages])

#     return image_sources

# # Check if an image URL is broken and handle encoding
# def check_image_link(args):
#     image_url, source_page = args
#     try:
#         encoded_url = sanitize_url(image_url)

#         # Print if there is an encoded character in the path (non-ASCII or space)
#         if '%' in encoded_url:
#             print(f"##### there is some issue in URL --> web page URL --> {source_page} --> URL of the image --> {encoded_url}")

#         # Make a HEAD request to check status
#         response = requests.head(encoded_url, timeout=5)
#         if response.status_code >= 400:
#             print(f"#### not found URL --> web page URL --> {source_page} --> URL of the image --> {encoded_url}")
#             return source_page, encoded_url, response.status_code
#     except Exception as e:
#         print(f"#### not found URL --> web page URL --> {source_page} --> URL of the image --> {image_url} (Exception: {e})")
#         return source_page, image_url, str(e)
#     return None

# # Check all image URLs for broken links
# def check_broken_images(image_sources):
#     broken = []
#     print("Checking broken images...")
#     with ThreadPoolExecutor(max_workers=10) as executor:
#         results = executor.map(check_image_link, image_sources.items())
#         for result in results:
#             if result:
#                 broken.append(result)
#     return broken

# # Main workflow
# def main(websites):
#     with open("output_for_broken.txt", "w", encoding="utf-8") as outfile:
#         for site in websites:
#             outfile.write(f"\n[Scanning Website] {site}\n")
#             print(f"\n[Scanning Website] {site}")
#             global visited_pages
#             visited_pages = set()

#             image_sources = crawl_website(site)
#             outfile.write(f"[Total Images Found] {len(image_sources)}\n")
#             print(f"[Total Images Found] {len(image_sources)}")

#             broken_images = check_broken_images(image_sources)
#             outfile.write(f"[Broken Images Found] {len(broken_images)}\n")
#             print(f"[Broken Images Found] {len(broken_images)}")

#             for page, img_url, error in broken_images:
#                 outfile.write(f"Page: {page}\n")
#                 outfile.write(f" - Broken Image: {img_url} --> {error}\n\n")
#                 print(f"Page: {page}")
#                 print(f" - Broken Image: {img_url} --> {error}")

#             outfile.write("***************************************\n")
#             print("***************************************")

# # Websites to scan
# if __name__ == "__main__":
#     websites = [
#         # "http://evisa-myanmar.com/",
#         # "http://evisa-to-kenya.org/",
#         # "http://georgia-e-visa.com/",
#         # "http://india-s-travel.com/",
#         # "http://japanevisa.net/",
#         # "http://malaysia-e-visa.com/",
#         # "http://nigeria-e-visa.com/",
#         # "http://vietnam-e-visas.com/"
#         "https://online.djibouti-evisa.com/djibouti-visa-types/",
#         "https://turkey-evisa.it.com/application-guide-form-es-apply-espanol/"
#     ]
#     main(websites)


import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse, quote
import string

visited_pages = set()
checked_image_urls = set()  # 🛑 Avoid duplicate checks

def sanitize_url(url):
    parsed = urlparse(url)
    encoded_path = quote(parsed.path)
    return urlunparse((parsed.scheme, parsed.netloc, encoded_path, parsed.params, parsed.query, parsed.fragment))

def check_image(image_url, source_page):
    if "email-protection" in image_url.lower():
        return  # 🔒 Skip protected image

    if image_url in checked_image_urls:
        return  # 🛑 Already checked

    checked_image_urls.add(image_url)

    try:
        encoded_url = sanitize_url(image_url)
        domain = f"{urlparse(source_page).scheme}://{urlparse(source_page).netloc}"

        issue_detected = False

        if '%' in encoded_url:
            print(f"\n[Website]: {domain}")
            print(f"[Page]: {source_page}")
            print(f"[Line with Issue]:")
            print(f" - Encoded URL Detected: {encoded_url}")
            issue_detected = True

        response = requests.head(encoded_url, timeout=5)
        if response.status_code >= 400:
            if not issue_detected:
                print(f"\n[Website]: {domain}")
                print(f"[Page]: {source_page}")
                print(f"[Line with Issue]:")
            print(f" - Broken Image: {encoded_url} --> {response.status_code}")

    except Exception as e:
        print(f"\n[Website]: {urlparse(source_page).scheme}://{urlparse(source_page).netloc}")
        print(f"[Page]: {source_page}")
        print(f"[Line with Issue]:")
        print(f" - Broken Image: {image_url} (Exception: {e})")

def check_anchor_issues(soup, page_url):
    anchors = soup.find_all('a', href=True)
    for anchor in anchors:
        try:
            href = anchor['href']
            if "email-protection" in href.lower():
                continue  # 🔒 Skip protected anchor

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

            # Smart skip if clean tag formatting
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

def crawl_page(url, base_domain):
    if "community" in url.lower():
        print(f"[Skipping community page] {url}")
        return []

    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            print(f"[Error] Could not load page: {url}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')

        # ✅ Check regular <img> tags
        images = soup.find_all('img', src=True)
        for img in images:
            full_img_url = urljoin(url, img['src'])
            check_image(full_img_url, url)

        # ✅ Check <picture> tags (source + img)
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

        # ✅ Check anchor tags
        check_anchor_issues(soup, url)

        # Extract internal links
        links = soup.find_all('a', href=True)
        page_links = [urljoin(url, a['href']) for a in links]
        page_links = [
            link for link in page_links
            if urlparse(link).netloc == base_domain and "community" not in link.lower()
        ]
        return page_links

    except Exception as e:
        print(f"[Error crawling page {url}]: {e}")
        return []

def crawl_website(start_url):
    domain = urlparse(start_url).netloc
    to_visit = [start_url]

    while to_visit:
        url = to_visit.pop()
        if url in visited_pages:
            continue
        visited_pages.add(url)
        print(f"\n[Crawling] {url}")
        links = crawl_page(url, domain)
        to_visit.extend([link for link in links if link not in visited_pages])

# Example usage
if __name__ == "__main__":
    crawl_website("https://turkey-evisa.it.com/")
