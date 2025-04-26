import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor
import time

visited_pages = set()

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
        
        return image_links, page_links
    except Exception as e:
        print(f"[Error fetching page] {url}: {e}")
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
        images, links = get_all_links_from_page(url)
        all_image_links.extend(images)
        to_visit.extend([link for link in links if link not in visited_pages])
    
    return list(set(all_image_links))  # remove duplicates

def check_image_link(url):
    print("checking the image links")
    try:
        print("no error in checking the image link",url)
        response = requests.head(url, timeout=5)
        print("checking the response", response.status_code)
        if response.status_code >= 400:
            print("URL-->", url, "status-->", response.status_code)
            return url, response.status_code
    except Exception as e:
        return url, str(e)
    # return None

def check_broken_images(image_urls):
    broken = []
    print("in broken_checking function")
    with ThreadPoolExecutor(max_workers=10) as executor:
        print("going to check the function")
        results = executor.map(check_image_link, image_urls)
        for result in results:
            print("checking the result", result)
            if result:
                print("results")
                print("printing the results if any", result)
                broken.append(result)
    print("okay")
    return broken

def main(websites):
    with open("output_for_broken.txt", "w", encoding="utf-8") as outfile:
        for site in websites:
            outfile.write(f"\n[Scanning Website] {site}\n")
            print(f"\n[Scanning Website] {site}")
            global visited_pages
            visited_pages = set()  # Reset for each site
            image_urls = crawl_website(site)
            outfile.write(f"[Total Images Found] {len(image_urls)}\n")
            print(f"[Total Images Found] {len(image_urls)}")
            broken_images = check_broken_images(image_urls)
            outfile.write(f"[Broken Images Found] {len(broken_images)}\n")
            print(f"[Broken Images Found] {len(broken_images)}")
            for url, error in broken_images:
                outfile.write(f" - {url} --> {error}\n")
                print(f" - {url} --> {error}")
            outfile.write("***************************************\n")
            print("***************************************")

if __name__ == "__main__":
    websites =[
 'http://visa-qatar.com/',
 'http://zambia-visa.com/',
 'http://zimbabwe-visa.com/',
 ]
    main(websites)
