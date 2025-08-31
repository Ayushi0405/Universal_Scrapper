#!/usr/bin/env python3
"""
Single-Page Web Scraper
A simplified web scraping tool using strict OOP principles for single page extraction only
"""

import requests
import cloudscraper
import sys
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from abc import ABC, abstractmethod
try:
    import httpx
except ImportError:
    httpx = None
try:
    from requests_html import HTMLSession
except ImportError:
    HTMLSession = None
try:
    from selenium_stealth import stealth
except ImportError:
    stealth = None


class ScrapingMethod(ABC):
    """Abstract base class for scraping methods"""
    
    def __init__(self, timeout=10):
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    @property
    @abstractmethod
    def method_name(self):
        """Return the name of this scraping method"""
        pass
    
    @abstractmethod
    def scrape(self, url):
        """Scrape the given URL and return content"""
        pass


class SimpleRequestsMethod(ScrapingMethod):
    """Basic requests method"""
    
    @property
    def method_name(self):
        return "Simple Requests"
    
    def scrape(self, url):
        try:
            print(f"Trying: {self.method_name} method...")
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"{self.method_name} failed: {str(e)}")
            return None


class RequestsWithHeadersMethod(ScrapingMethod):
    """Requests with full headers"""
    
    @property
    def method_name(self):
        return "Requests with Headers"
    
    def scrape(self, url):
        try:
            print(f"Trying: {self.method_name} method...")
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"{self.method_name} failed: {str(e)}")
            return None


class HTTPXMethod(ScrapingMethod):
    """HTTPX with HTTP/2 support"""
    
    @property
    def method_name(self):
        return "HTTPX HTTP/2"
    
    def scrape(self, url):
        if not httpx:
            print("HTTPX skipped: httpx not installed")
            return None
            
        try:
            print(f"Trying: {self.method_name} method...")
            with httpx.Client(http2=True, timeout=self.timeout) as client:
                response = client.get(url, headers=self.headers)
                response.raise_for_status()
                return response.text
        except Exception as e:
            print(f"{self.method_name} failed: {str(e)}")
            return None


class CloudScraperMethod(ScrapingMethod):
    """CloudScraper for Cloudflare bypass"""
    
    @property
    def method_name(self):
        return "CloudScraper"
    
    def scrape(self, url):
        try:
            print(f"Trying: {self.method_name} method...")
            scraper = cloudscraper.create_scraper()
            response = scraper.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"{self.method_name} failed: {str(e)}")
            return None


class CloudScraperWithHeadersMethod(ScrapingMethod):
    """CloudScraper with custom headers"""
    
    @property
    def method_name(self):
        return "CloudScraper with Headers"
    
    def scrape(self, url):
        try:
            print(f"Trying: {self.method_name} method...")
            scraper = cloudscraper.create_scraper()
            response = scraper.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"{self.method_name} failed: {str(e)}")
            return None


class RequestsHTMLMethod(ScrapingMethod):
    """Requests-HTML for JavaScript rendering"""
    
    @property
    def method_name(self):
        return "Requests-HTML"
    
    def scrape(self, url):
        if not HTMLSession:
            print("Requests-HTML skipped: requests-html not installed")
            return None
            
        try:
            print(f"Trying: {self.method_name} method...")
            session = HTMLSession()
            response = session.get(url, timeout=self.timeout)
            response.html.render(timeout=10)
            return response.html.html
        except Exception as e:
            print(f"{self.method_name} failed: {str(e)}")
            return None


class SeleniumMethod(ScrapingMethod):
    """Selenium WebDriver method"""
    
    @property
    def method_name(self):
        return "Selenium WebDriver"
    
    def scrape(self, url):
        driver = None
        try:
            print(f"Trying: {self.method_name} method...")
            
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument(f"--user-agent={self.headers['User-Agent']}")
            options.add_experimental_option('useAutomationExtension', False)
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            
            driver = webdriver.Chrome(options=options)
            driver.set_page_load_timeout(self.timeout)
            driver.get(url)
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            return driver.page_source
            
        except Exception as e:
            print(f"{self.method_name} failed: {str(e)}")
            return None
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass


class SeleniumStealthMethod(ScrapingMethod):
    """Selenium with stealth mode"""
    
    @property
    def method_name(self):
        return "Selenium Stealth Mode"
    
    def scrape(self, url):
        if not stealth:
            print("Selenium Stealth Mode skipped: selenium-stealth not installed")
            return None
            
        driver = None
        try:
            print(f"Trying: {self.method_name} method...")
            
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            driver = webdriver.Chrome(options=options)
            stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True)
            
            driver.set_page_load_timeout(self.timeout)
            driver.get(url)
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            return driver.page_source
            
        except Exception as e:
            print(f"{self.method_name} failed: {str(e)}")
            return None
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass


class CookiePersistentMethod(ScrapingMethod):
    """Requests with persistent cookies"""
    
    @property
    def method_name(self):
        return "Cookie Persistent Session"
    
    def scrape(self, url):
        try:
            print(f"Trying: {self.method_name} method...")
            session = requests.Session()
            session.headers.update(self.headers)
            
            response = session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.text
            
        except Exception as e:
            print(f"{self.method_name} failed: {str(e)}")
            return None


class TorRequestsMethod(ScrapingMethod):
    """Requests through Tor network"""
    
    @property
    def method_name(self):
        return "Tor Network Requests"
    
    def scrape(self, url):
        try:
            print(f"Trying: {self.method_name} method...")
            
            proxies = {
                'http': 'socks5://127.0.0.1:9050',
                'https': 'socks5://127.0.0.1:9050'
            }
            
            response = requests.get(url, proxies=proxies, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.text
            
        except Exception as e:
            print(f"{self.method_name} failed: {str(e)} (Is Tor running?)")
            return None


class SlowRequestsMethod(ScrapingMethod):
    """Very slow requests to avoid rate limiting"""
    
    @property
    def method_name(self):
        return "Slow Requests (Anti-Rate-Limit)"
    
    def scrape(self, url):
        try:
            print(f"Trying: {self.method_name} method...")
            
            time.sleep(random.uniform(3, 7))
            
            session = requests.Session()
            session.headers.update(self.headers)
            
            response = session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            return response.text
            
        except Exception as e:
            print(f"{self.method_name} failed: {str(e)}")
            return None


class MultipleHeadersMethod(ScrapingMethod):
    """Requests with multiple common headers"""
    
    @property
    def method_name(self):
        return "Multiple Headers"
    
    def scrape(self, url):
        try:
            print(f"Trying: {self.method_name} method...")
            
            extended_headers = {
                **self.headers,
                'DNT': '1',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
                'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"'
            }
            
            session = requests.Session()
            session.headers.update(extended_headers)
            
            response = session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            return response.text
            
        except Exception as e:
            print(f"{self.method_name} failed: {str(e)}")
            return None


class BrowserMimicMethod(ScrapingMethod):
    """Mimics real browser behavior with referrer"""
    
    @property
    def method_name(self):
        return "Browser Mimic"
    
    def scrape(self, url):
        try:
            print(f"Trying: {self.method_name} method...")
            
            session = requests.Session()
            
            # First visit Google to get referrer
            google_headers = {
                'User-Agent': self.headers['User-Agent'],
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            session.headers.update(google_headers)
            session.get('https://www.google.com', timeout=self.timeout)
            
            time.sleep(random.uniform(1, 3))
            
            # Now visit the target site with Google as referrer
            target_headers = {
                **self.headers,
                'Referer': 'https://www.google.com/'
            }
            session.headers.update(target_headers)
            
            response = session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            return response.text
            
        except Exception as e:
            print(f"{self.method_name} failed: {str(e)}")
            return None


class URLValidator:
    """Validates and formats URLs"""
    
    def validate_and_format_url(self, url):
        """Validate URL and add protocol if missing"""
        if not url:
            raise ValueError("URL cannot be empty")
        
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        parsed = urlparse(url)
        if not parsed.netloc:
            raise ValueError(f"Invalid URL: {url}")
        
        return url


class ContentValidator:
    """Validates scraped content"""
    
    def is_valid_content(self, content):
        """Check if content is valid and substantial"""
        if not content:
            return False
        
        content = content.strip()
        if len(content) < 100:  # Too short to be meaningful
            return False
        
        # Check for basic HTML structure or substantial text
        html_indicators = ['<html', '<body', '<div', '<p', '<span']
        if any(indicator in content.lower() for indicator in html_indicators):
            return True
        
        # If not HTML, check for substantial text content
        if len(content) > 500:
            return True
        
        return False


class FileManager:
    """Manages file operations"""
    
    def save_content(self, content, filename, url):
        """Save content to file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"<!-- Scraped from: {url} -->\n")
                f.write(f"<!-- Scraped at: {time.strftime('%Y-%m-%d %H:%M:%S')} -->\n\n")
                f.write(content)
            
            print(f"Content saved to: {filename}")
            return True
            
        except Exception as e:
            print(f"Failed to save content: {str(e)}")
            return False


class UserAgentRotator:
    """Rotates user agents to avoid detection"""
    
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59'
        ]
    
    def get_random_user_agent(self):
        """Get a random user agent"""
        return random.choice(self.user_agents)


class RetryMechanism:
    """Handles retry logic with exponential backoff"""
    
    def __init__(self, max_retries=3, base_delay=1):
        self.max_retries = max_retries
        self.base_delay = base_delay
    
    def retry_with_backoff(self, func, *args, **kwargs):
        """Retry function with exponential backoff"""
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries:
                    raise e
                
                delay = self.base_delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"Retry {attempt + 1}/{self.max_retries} after {delay:.1f}s delay...")
                time.sleep(delay)
        
        return None


class SinglePageScraper:
    """Single-page web scraper that orchestrates all scraping methods"""
    
    def __init__(self, timeout=10, max_retries=3, aggressive_mode=True):
        self.timeout = timeout
        self.max_retries = max_retries
        self.file_manager = FileManager()
        self.url_validator = URLValidator()
        self.content_validator = ContentValidator()
        self.user_agent_rotator = UserAgentRotator()
        self.retry_mechanism = RetryMechanism(max_retries=max_retries)
        self.methods = self._initialize_methods(aggressive_mode)
    
    def _initialize_methods(self, aggressive_mode):
        """Initialize all scraping methods"""
        methods = [
            SimpleRequestsMethod(self.timeout),
            RequestsWithHeadersMethod(self.timeout),
            HTTPXMethod(self.timeout),
            CloudScraperMethod(self.timeout),
            CloudScraperWithHeadersMethod(self.timeout),
            RequestsHTMLMethod(self.timeout),
            SeleniumMethod(self.timeout),
            SeleniumStealthMethod(self.timeout),
            CookiePersistentMethod(self.timeout),
            TorRequestsMethod(self.timeout)
        ]
        
        if aggressive_mode:
            methods.extend([
                SlowRequestsMethod(self.timeout),
                MultipleHeadersMethod(self.timeout),
                BrowserMimicMethod(self.timeout)
            ])
        
        return methods
    
    def scrape_website(self, url, save_to_file=None, concurrent=True):
        """
        Ultra-robust method to scrape single website page using multiple methods
        """
        try:
            formatted_url = self.url_validator.validate_and_format_url(url)
        except ValueError as e:
            print(f"URL Error: {str(e)}")
            return None
        
        print(f"Starting single-page scraping: {formatted_url}")
        print(f"Using {len(self.methods)} methods {'CONCURRENTLY' if concurrent else 'SEQUENTIALLY'}")
        print("-" * 60)
        
        if concurrent:
            return self._scrape_concurrent(formatted_url, save_to_file)
        else:
            return self._scrape_sequential(formatted_url, save_to_file)
    
    def _scrape_concurrent(self, url, save_to_file):
        """Scrape using all methods concurrently"""
        print("Launching all scraping methods in parallel...")
        
        # Use a lock to ensure only one success is processed
        success_lock = threading.Lock()
        success_result = {'content': None, 'method_name': None}
        
        def scrape_method_wrapper(method):
            """Wrapper to handle method execution with early termination"""
            if success_result['content']:  # Early termination
                return None
                
            try:
                print(f" Starting {method.method_name}...")
                content = self.retry_mechanism.retry_with_backoff(
                    self._scrape_with_method, method, url
                )
                
                if self.content_validator.is_valid_content(content):
                    with success_lock:
                        if not success_result['content']:  # First to succeed
                            success_result['content'] = content
                            success_result['method_name'] = method.method_name
                            print(f" FIRST SUCCESS: {method.method_name} ({len(content):,} chars)")
                    return content
                else:
                    print(f" {method.method_name}: Invalid content")
                    return None
                    
            except Exception as e:
                print(f" {method.method_name}: {str(e)}")
                return None
        
        # Execute all methods concurrently with a reasonable thread pool
        max_workers = min(len(self.methods), 8)  # Don't overwhelm the system
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_method = {executor.submit(scrape_method_wrapper, method): method 
                              for method in self.methods}
            
            # Process results as they complete
            for future in as_completed(future_to_method):
                if success_result['content']:
                    # Cancel remaining tasks once we have success
                    for remaining_future in future_to_method:
                        if remaining_future != future:
                            remaining_future.cancel()
                    break
        
        # Handle results
        if success_result['content']:
            print(f" CONCURRENT SUCCESS with {success_result['method_name']}!")
            print(f" Content length: {len(success_result['content']):,} characters")
            
            if save_to_file:
                self.file_manager.save_content(success_result['content'], save_to_file, url)
            
            return success_result['content']
        else:
            print("\n All concurrent methods failed")
            return None
    
    def _scrape_sequential(self, url, save_to_file):
        """Sequential scraping method"""
        for method_index, method in enumerate(self.methods, 1):
            print(f"\n[Method {method_index}/{len(self.methods)}] {method.method_name}")
            
            try:
                content = self.retry_mechanism.retry_with_backoff(
                    self._scrape_with_method, method, url
                )
                
                if self.content_validator.is_valid_content(content):
                    print(f" SUCCESS with {method.method_name}!")
                    print(f" Content length: {len(content):,} characters")
                    
                    if save_to_file:
                        self.file_manager.save_content(content, save_to_file, url)
                    
                    return content
                elif content:
                    print(f"  {method.method_name} returned content but it's too short ({len(content)} chars)")
                else:
                    print(f" {method.method_name} returned no content")
                    
            except Exception as e:
                print(f" {method.method_name} failed completely: {str(e)}")
                continue
        
        print("\n CRITICAL: All methods exhausted - website appears to be heavily protected")
        print("  Consider using VPN, different network, or manual browser inspection")
        return None
    
    def _scrape_with_method(self, method, url):
        """Internal method to scrape with dynamic user agent rotation"""
        if hasattr(method, 'headers') and method.headers:
            method.headers['User-Agent'] = self.user_agent_rotator.get_random_user_agent()
        
        time.sleep(random.uniform(0.5, 2.0))
        
        return method.scrape(url)


class CommandLineInterface:
    """Handles command line interface operations"""
    
    def __init__(self):
        self.scraper = SinglePageScraper(aggressive_mode=True)
    
    def parse_arguments(self, args):
        """Parse command line arguments - SINGLE PAGE MODE ONLY"""
        if len(args) < 2:
            self.show_usage()
            return None, None, True, True
        
        url = args[1]
        output_file = None
        aggressive = True  # Default to aggressive mode for better success rate
        concurrent = True  # Default to concurrent for speed
        
        # Generate automatic output filename based on URL
        domain = url.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0].replace('.', '_')
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        
        # Parse remaining arguments (optional overrides)
        i = 2
        while i < len(args):
            arg = args[i]
            if arg in ['--aggressive', '-a']:
                aggressive = True
            elif arg in ['--sequential', '-s']:
                concurrent = False
            elif not arg.startswith('-'):
                output_file = arg
            i += 1
        
        # Auto-generate output file if not specified
        if not output_file:
            output_file = f"{domain}_single_page_{timestamp}.html"
        
        return url, output_file, aggressive, concurrent
    
    def show_usage(self):
        """Show usage instructions"""
        print("  SINGLE-PAGE Web Scraper")
        print("=" * 35)
        print(" SCRAPE ONLY THE SPECIFIC PAGE YOU PROVIDE!")
        print("")
        print("BASIC USAGE:")
        print("  python scrapper.py <URL>")
        print("")
        print("EXAMPLES:")
        print("  python scrapper.py https://example.com/specific-page")
        print("  python scrapper.py https://www.ambitionbox.com/company/tcs")
        print("  python scrapper.py https://any-website.com/single-article")
        print("")
        print("WHAT HAPPENS:")
        print("   Scrapes ONLY the exact page URL you provide")
        print("   Uses aggressive mode for maximum success rate")
        print("   Tries 13+ different scraping methods concurrently")
        print("   Auto-generates filename with timestamp")
        print("   Handles JavaScript, Cloudflare, anti-bot protection")
        print("   NO PAGINATION - Only single page extraction")
        print("")
        print("OPTIONAL FLAGS:")
        print("  python scrapper.py <URL> [custom_filename.html]")
        print("  python scrapper.py <URL> --sequential     (slower but safer)")
        print("")
        print(" OUTPUT: HTML file with ONLY the content from the specific page")
    
    def display_content(self, content, max_length=1000):
        """Display scraped content"""
        if content:
            print("\n" + "="*60)
            print(" SCRAPED CONTENT PREVIEW")
            print("="*60)
            preview = content[:max_length] + "..." if len(content) > max_length else content
            print(preview)
            print("="*60)
    
    def run(self, args):
        """Main CLI execution method"""
        parsed_args = self.parse_arguments(args)
        if not parsed_args[0]:  # url is None
            return 1
            
        url, output_file, aggressive, concurrent = parsed_args
        
        print(" SINGLE-PAGE WEB SCRAPER ACTIVATED!")
        print("=" * 45)
        print(f" Target URL: {url}")
        print(f" Mode: {'AGGRESSIVE' if aggressive else 'STANDARD'}")
        print(f" Execution: {'CONCURRENT' if concurrent else 'SEQUENTIAL'} (13+ methods)")
        print(f" Auto-Save: {output_file}")
        print("")
        print(" Scraping ONLY the specific page you provided...")
        print("")
        
        # Single page scraping
        content = self.scraper.scrape_website(url, output_file, concurrent=concurrent)
        
        if content:
            if not output_file:
                self.display_content(content)
            print(f"\nSINGLE-PAGE SCRAPING SUCCESSFUL!")
            print(f"Content extracted: {len(content):,} characters")
            print(f"HTML tags found: {content.count('<')}")
            print(f"Method execution: {concurrent and 'CONCURRENT' or 'SEQUENTIAL'}")
            return 0
        else:
            print("\nSCRAPING FAILED - All methods exhausted")
            print("Suggestions:")
            print("   - Try --sequential if concurrent mode failed")
            print("   - Check if the website requires authentication")
            print("   - Verify the URL is accessible from your network")
            print("   - Some sites may require human verification")
            return 1


def main():
    """Entry point of the application"""
    cli = CommandLineInterface()
    exit_code = cli.run(sys.argv)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()