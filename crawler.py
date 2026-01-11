import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import tldextract
import validators


class Crawler:

    def validate_url(self, url):
        if not validators.url(url):
            return False
        return True

    def fetch_content_from_url(self, url):
        is_valid_url = self.validate_url(url)
        if not is_valid_url:
            print(f"Invalid URL: {url}")
            return None
        try:
            resp = requests.get(
                url, timeout=5, headers={"User-Agent": "rag-chatbot/5.0"}
            )
            resp.raise_for_status()
            return resp.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def is_same_domain(self, base_url, other_url):
        base = tldextract.extract(base_url)
        other = tldextract.extract(other_url)
        return (base.domain, base.suffix) == (other.domain, other.suffix)

    def extract_links(self, base_url, html_content):
        soup = BeautifulSoup(html_content, "html.parser")
        links = set()
        for link in soup.find_all("a", href=True):
            absolute_link = urljoin(base_url, link["href"])
            parsed_link = urlparse(absolute_link)
            if parsed_link.scheme in ["http", "https"]:
                links.add(absolute_link)
        return links

    def crawl(self, url, max_pages=10, max_depth=5):
        visited = set()
        to_visit = [(url, 0)]
        all_content = []

        while to_visit and len(visited) < max_pages:
            current_url, depth = to_visit.pop(0)
            if current_url in visited or depth > max_depth:
                continue

            print(f"Crawling page {len(visited)+1}: {current_url} at depth {depth}")
            content = self.fetch_content_from_url(url=current_url)
            if content:
                all_content.append((current_url, content))
                visited.add(current_url)

                hyperlinks = self.extract_links(
                    base_url=current_url, html_content=content
                )
                for link in hyperlinks:
                    if link not in visited and self.is_same_domain(url, link):
                        to_visit.append((link, depth + 1))

        return all_content
