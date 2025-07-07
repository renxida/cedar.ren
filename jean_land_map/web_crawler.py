#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import time
import argparse
import os
from typing import Set, Dict, List
import logging

class ResumableWebCrawler:
    def __init__(self, start_url: str, max_depth: int = 5, delay: float = 1.0, 
                 state_file: str = "crawler_state.json"):
        self.start_url = start_url
        self.max_depth = max_depth
        self.delay = delay
        self.state_file = state_file
        self.domain = urlparse(start_url).netloc
        
        # State tracking
        self.visited_urls: Set[str] = set()
        self.url_queue: List[Dict] = []
        self.crawled_data: Dict[str, Dict] = {}
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # Load existing state if available
        self.load_state()
    
    def save_state(self):
        """Save current crawling state to file"""
        state = {
            'visited_urls': list(self.visited_urls),
            'url_queue': self.url_queue,
            'crawled_data': self.crawled_data,
            'start_url': self.start_url,
            'max_depth': self.max_depth
        }
        
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
        self.logger.info(f"State saved to {self.state_file}")
    
    def load_state(self):
        """Load previous crawling state if exists"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                
                self.visited_urls = set(state.get('visited_urls', []))
                self.url_queue = state.get('url_queue', [])
                self.crawled_data = state.get('crawled_data', {})
                
                self.logger.info(f"Resumed from {self.state_file}: {len(self.visited_urls)} URLs visited, {len(self.url_queue)} URLs queued")
                return True
            except Exception as e:
                self.logger.error(f"Error loading state: {e}")
                return False
        return False
    
    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and within the same domain"""
        try:
            parsed = urlparse(url)
            return (parsed.netloc == self.domain and 
                    parsed.scheme in ['http', 'https'] and
                    url not in self.visited_urls)
        except:
            return False
    
    def extract_links(self, html: str, base_url: str) -> List[str]:
        """Extract all links from HTML content"""
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(base_url, href)
            
            if self.is_valid_url(absolute_url):
                links.append(absolute_url)
        
        return links
    
    def crawl_url(self, url: str) -> Dict:
        """Crawl a single URL and return page data"""
        try:
            self.logger.info(f"Crawling: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; WebCrawler/1.0)'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Extract page information
            soup = BeautifulSoup(response.text, 'html.parser')
            
            page_data = {
                'url': url,
                'title': soup.title.string.strip() if soup.title else '',
                'status_code': response.status_code,
                'content_length': len(response.text),
                'links_found': [],
                'crawl_time': time.time()
            }
            
            # Extract links
            links = self.extract_links(response.text, url)
            page_data['links_found'] = links
            
            return page_data
            
        except Exception as e:
            self.logger.error(f"Error crawling {url}: {e}")
            return {
                'url': url,
                'error': str(e),
                'status_code': -1,
                'crawl_time': time.time()
            }
    
    def crawl(self):
        """Main crawling function"""
        # Initialize queue if empty
        if not self.url_queue and not self.visited_urls:
            self.url_queue.append({'url': self.start_url, 'depth': 0})
        
        try:
            while self.url_queue:
                current = self.url_queue.pop(0)
                url = current['url']
                depth = current['depth']
                
                # Skip if already visited or depth exceeded
                if url in self.visited_urls or depth > self.max_depth:
                    continue
                
                # Mark as visited
                self.visited_urls.add(url)
                
                # Crawl the URL
                page_data = self.crawl_url(url)
                self.crawled_data[url] = page_data
                
                # Add new URLs to queue if not at max depth
                if depth < self.max_depth and 'links_found' in page_data:
                    for link in page_data['links_found']:
                        if link not in self.visited_urls:
                            self.url_queue.append({'url': link, 'depth': depth + 1})
                
                # Save state periodically
                if len(self.visited_urls) % 10 == 0:
                    self.save_state()
                
                # Respect delay
                time.sleep(self.delay)
                
                self.logger.info(f"Progress: {len(self.visited_urls)} crawled, {len(self.url_queue)} queued")
        
        except KeyboardInterrupt:
            self.logger.info("Crawling interrupted by user")
        except Exception as e:
            self.logger.error(f"Crawling error: {e}")
        finally:
            # Always save final state
            self.save_state()
    
    def export_results(self, output_file: str = "crawl_results.json"):
        """Export crawling results to JSON file"""
        results = {
            'summary': {
                'total_urls_crawled': len(self.visited_urls),
                'total_urls_queued': len(self.url_queue),
                'start_url': self.start_url,
                'max_depth': self.max_depth,
                'domain': self.domain
            },
            'crawled_data': self.crawled_data
        }
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        self.logger.info(f"Results exported to {output_file}")
    
    def print_summary(self):
        """Print crawling summary"""
        print(f"\n=== Crawling Summary ===")
        print(f"Domain: {self.domain}")
        print(f"Start URL: {self.start_url}")
        print(f"Max Depth: {self.max_depth}")
        print(f"URLs Crawled: {len(self.visited_urls)}")
        print(f"URLs Queued: {len(self.url_queue)}")
        print(f"Successful Crawls: {len([d for d in self.crawled_data.values() if d.get('status_code', -1) == 200])}")
        print(f"Failed Crawls: {len([d for d in self.crawled_data.values() if d.get('status_code', -1) != 200])}")

def main():
    parser = argparse.ArgumentParser(description='Resumable Web Crawler')
    parser.add_argument('--url', default='https://www.jean.land/', help='Starting URL to crawl')
    parser.add_argument('--depth', type=int, default=5, help='Maximum crawling depth')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between requests (seconds)')
    parser.add_argument('--state-file', default='crawler_state.json', help='State file for resume functionality')
    parser.add_argument('--output', default='crawl_results.json', help='Output file for results')
    parser.add_argument('--resume', action='store_true', help='Resume from existing state file')
    
    args = parser.parse_args()
    
    # Create crawler instance
    crawler = ResumableWebCrawler(
        start_url=args.url,
        max_depth=args.depth,
        delay=args.delay,
        state_file=args.state_file
    )
    
    print(f"Starting crawl of {args.url} with max depth {args.depth}")
    print(f"State file: {args.state_file}")
    print(f"Delay between requests: {args.delay}s")
    print("Press Ctrl+C to interrupt and save state\n")
    
    # Start crawling
    crawler.crawl()
    
    # Export results and print summary
    crawler.export_results(args.output)
    crawler.print_summary()

if __name__ == "__main__":
    main()