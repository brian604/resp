import requests
import json
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import time
import xml.etree.ElementTree as ET
from typing import Optional, List, Dict


class Arxiv(object):
    def __init__(self):
        self.base_url = "http://export.arxiv.org/api/query"
        self.search_url = "https://arxiv.org/search/"

    def arxiv_payload(self, keyword, size=50, start=0):
        """Legacy method using web scraping."""
        headers = {
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Mobile Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Referer": "https://arxiv.org/search/?query=Multi-label+text+classification&searchtype=all&abstracts=show&order=&size=50&start=200",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        }

        params = (
            ("searchtype", "all"),
            ("query", keyword.lower()),
            ("abstracts", "show"),
            ("size", str(size)),
            ("order", ""),
            ("start", str(start)),
        )
        response = requests.get(
            self.search_url, headers=headers, params=params
        )
        soup = BeautifulSoup(response.text, "html.parser")

        return soup

    def arxiv_html_fetch(self, soup, include_abstract=True):
        """Enhanced HTML parsing with abstract extraction."""
        final_result = []
        final_out = soup.find_all("li", {"class": "arxiv-result"})

        for paper in final_out:
            temp_result = {}

            # Extract title
            title_elem = paper.find("p", {"class": "title is-5 mathjax"})
            if title_elem:
                temp_result["title"] = title_elem.text.strip()

            # Extract link
            link_elem = paper.find("p", {"class": "list-title is-inline-block"})
            if link_elem:
                link = link_elem.find("a", href=True)
                if link:
                    temp_result["link"] = link["href"]

            # Extract abstract if requested
            if include_abstract:
                abstract_elem = paper.find("span", {"class": "abstract-full"})
                if not abstract_elem:
                    abstract_elem = paper.find("span", {"class": "abstract-short"})
                if abstract_elem:
                    temp_result["abstract"] = abstract_elem.text.strip()
                else:
                    temp_result["abstract"] = ""

            # Extract authors
            authors_elem = paper.find("p", {"class": "authors"})
            if authors_elem:
                authors = [a.text.strip() for a in authors_elem.find_all("a")]
                temp_result["authors"] = ", ".join(authors)

            # Extract publication date
            submitted_elem = paper.find("p", {"class": "is-size-7"})
            if submitted_elem:
                temp_result["submitted"] = submitted_elem.text.strip()

            if temp_result:  # Only add if we got some data
                final_result.append(temp_result)

        df = pd.DataFrame(final_result)
        return df

    def arxiv_api_query(
        self,
        search_query: str,
        max_results: int = 50,
        start: int = 0,
        sort_by: str = "relevance"
    ) -> List[Dict]:
        """
        Use official arXiv API for better results.

        Args:
            search_query: Search query (can use arXiv query syntax)
            max_results: Maximum number of results
            start: Starting index for pagination
            sort_by: Sort order ("relevance", "lastUpdatedDate", "submittedDate")

        Returns:
            List of paper dictionaries
        """
        params = {
            'search_query': f'all:{search_query}',
            'start': start,
            'max_results': max_results,
            'sortBy': sort_by,
            'sortOrder': 'descending'
        }

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()

            # Parse XML response
            root = ET.fromstring(response.content)

            # Extract namespace
            ns = {'atom': 'http://www.w3.org/2005/Atom',
                  'arxiv': 'http://arxiv.org/schemas/atom'}

            papers = []
            for entry in root.findall('atom:entry', ns):
                paper = {}

                # Title
                title_elem = entry.find('atom:title', ns)
                if title_elem is not None:
                    paper['title'] = title_elem.text.strip().replace('\n', ' ')

                # Abstract
                summary_elem = entry.find('atom:summary', ns)
                if summary_elem is not None:
                    paper['abstract'] = summary_elem.text.strip().replace('\n', ' ')

                # Link
                link_elem = entry.find('atom:id', ns)
                if link_elem is not None:
                    paper['link'] = link_elem.text.strip()

                # Authors
                authors = []
                for author in entry.findall('atom:author', ns):
                    name_elem = author.find('atom:name', ns)
                    if name_elem is not None:
                        authors.append(name_elem.text.strip())
                paper['authors'] = ', '.join(authors)

                # Published date
                published_elem = entry.find('atom:published', ns)
                if published_elem is not None:
                    paper['published'] = published_elem.text.strip()

                # Updated date
                updated_elem = entry.find('atom:updated', ns)
                if updated_elem is not None:
                    paper['updated'] = updated_elem.text.strip()

                # Categories
                categories = []
                for category in entry.findall('atom:category', ns):
                    cat_term = category.get('term')
                    if cat_term:
                        categories.append(cat_term)
                paper['categories'] = ', '.join(categories)

                papers.append(paper)

            return papers

        except Exception as e:
            print(f"Error querying arXiv API: {e}")
            return []

    def arxiv(
        self,
        keyword: str,
        max_pages: int = 5,
        api_wait: int = 3,
        use_api: bool = True,
        include_abstract: bool = True
    ):
        """
        Main arxiv search function with API and scraping support.

        Args:
            keyword: Search keyword
            max_pages: Number of pages to fetch
            api_wait: Wait time between requests (seconds)
            use_api: Use official arXiv API (True) or web scraping (False)
            include_abstract: Include abstracts in results

        Returns:
            DataFrame with paper information
        """
        if use_api:
            # Use official arXiv API
            all_papers = []
            for page in tqdm(range(max_pages)):
                papers = self.arxiv_api_query(
                    keyword,
                    max_results=50,
                    start=page * 50
                )
                if papers:
                    all_papers.extend(papers)
                    time.sleep(api_wait)
                else:
                    break

            if all_papers:
                df = pd.DataFrame(all_papers)
                return df.reset_index(drop=True)
            else:
                return pd.DataFrame()
        else:
            # Use web scraping (legacy method)
            all_pages = []
            for page in tqdm(range(max_pages)):
                arxiv_pay_load = self.arxiv_payload(keyword, start=page * 50)
                arxiv_soup = self.arxiv_html_fetch(arxiv_pay_load, include_abstract)
                all_pages.append(arxiv_soup)
                time.sleep(api_wait)

            if all_pages:
                df = pd.concat(all_pages)
                return df.reset_index(drop=True)
            else:
                return pd.DataFrame()
