"""
Universal Scraper Module
A Python module for AI-powered web scraping with customizable field extraction.

Usage:
    from universal_scraper import UniversalScraper
    
    scraper = UniversalScraper(api_key="your_gemini_api_key")
    scraper.set_fields(["company_name", "job_title", "apply_link", "salary_range"])
    data = scraper.scrape_url("https://example.com/jobs")
"""

import logging
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from urllib.parse import urlparse

from html_fetcher import HtmlFetcher
from html_cleaner import HtmlCleaner
from data_extractor import DataExtractor
import google.generativeai as genai


class UniversalScraper:
    """
    A modular web scraping system that fetches HTML, cleans it, and extracts 
    structured data using AI with customizable field extraction.
    """
    
    def __init__(self, api_key: Optional[str] = None, 
                 temp_dir: str = "temp", 
                 output_dir: str = "output",
                 log_level: int = logging.INFO,
                 model_name: Optional[str] = None):
        """
        Initialize the Universal Scraper.
        
        Args:
            api_key: Gemini API key (optional, can use GEMINI_API_KEY env var)
            temp_dir: Directory for temporary files
            output_dir: Directory for output files
            log_level: Logging level
            model_name: Gemini model name (default: 'gemini-2.0-flash-exp')
        """
        self.setup_logging(log_level)
        self.logger = logging.getLogger(__name__)
        self.temp_dir = temp_dir
        self.output_dir = output_dir
        self.api_key = api_key
        self.model_name = model_name
        self.extraction_fields = ["company_name", "job_title", "apply_link", "salary_range"]
        
        # Create directories
        os.makedirs(temp_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize modules
        self.fetcher = HtmlFetcher(temp_dir=temp_dir)
        self.cleaner = HtmlCleaner(temp_dir=temp_dir)
        
        # Initialize extractor with custom fields support
        self.extractor = CustomDataExtractor(
            api_key=api_key, 
            temp_dir=temp_dir, 
            output_dir=output_dir,
            fields=self.extraction_fields,
            model_name=model_name
        )
    
    def setup_logging(self, level: int):
        """Setup logging configuration"""
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def set_fields(self, fields: List[str]) -> None:
        """
        Set the fields to extract from web pages.
        
        Args:
            fields: List of field names to extract (e.g., ["company_name", "job_title"])
        """
        if not fields or not isinstance(fields, list):
            raise ValueError("Fields must be a non-empty list")
        
        self.extraction_fields = fields
        self.extractor.set_fields(fields)
        self.logger.info(f"Extraction fields updated: {fields}")
    
    def get_fields(self) -> List[str]:
        """
        Get the currently configured extraction fields.
        
        Returns:
            List of field names currently configured for extraction
        """
        return self.extraction_fields.copy()
    
    def get_model_name(self) -> str:
        """
        Get the currently configured Gemini model name.
        
        Returns:
            Name of the Gemini model being used
        """
        return self.extractor.model_name
    
    def set_model_name(self, model_name: str) -> None:
        """
        Change the Gemini model name.
        
        Args:
            model_name: Name of the Gemini model to use (e.g., 'gemini-pro', 'gemini-2.0-flash-exp')
        """
        self.model_name = model_name
        self.extractor.model_name = model_name
        self.extractor.model = genai.GenerativeModel(model_name)
        self.logger.info(f"Model changed to: {model_name}")
    
    def scrape_url(self, url: str, save_to_file: bool = False, 
                  output_filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Scrape a single URL and return extracted data.
        
        Args:
            url: URL to scrape
            save_to_file: Whether to save results to a file
            output_filename: Custom output filename (optional)
            
        Returns:
            Dictionary containing extracted data and metadata
        """
        self.logger.info(f"Starting scraping for: {url}")
        
        if not self._validate_url(url):
            raise ValueError(f"Invalid URL format: {url}")
        
        try:
            # Step 1: Fetch HTML
            raw_html = self.fetcher.fetch_html(url)
            
            # Step 2: Clean HTML
            cleaned_html = self.cleaner.clean_html(raw_html, url=url)
            
            # Step 3: Extract structured data
            extracted_data = self.extractor.extract_data(cleaned_html, url)
            
            result = {
                "url": url,
                "timestamp": datetime.now().isoformat(),
                "fields": self.extraction_fields,
                "data": extracted_data,
                "metadata": {
                    "raw_html_length": len(raw_html),
                    "cleaned_html_length": len(cleaned_html),
                    "items_extracted": len(extracted_data) if isinstance(extracted_data, list) else 1
                }
            }
            
            # Optionally save to file
            if save_to_file:
                filename = output_filename or self._generate_filename(url)
                filepath = self._save_data(result, filename)
                result["saved_to"] = filepath
            
            self.logger.info(f"Successfully extracted data from {url}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to scrape {url}: {str(e)}")
            raise
    
    def scrape_multiple_urls(self, urls: List[str], save_to_files: bool = True) -> List[Dict[str, Any]]:
        """
        Scrape multiple URLs.
        
        Args:
            urls: List of URLs to scrape
            save_to_files: Whether to save results to individual files
            
        Returns:
            List of results for each URL
        """
        results = []
        
        for i, url in enumerate(urls, 1):
            self.logger.info(f"Processing URL {i}/{len(urls)}: {url}")
            
            try:
                result = self.scrape_url(url, save_to_file=save_to_files)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Failed to scrape {url}: {str(e)}")
                results.append({
                    "url": url,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        return results
    
    def _validate_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            parsed = urlparse(url)
            return all([parsed.scheme, parsed.netloc]) and parsed.scheme in ['http', 'https']
        except Exception:
            return False
    
    def _generate_filename(self, url: str) -> str:
        """Generate filename based on URL"""
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '').replace('.', '_')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{domain}_{timestamp}.json"
    
    def _save_data(self, data: Dict[str, Any], filename: str) -> str:
        """Save data to JSON file"""
        if not os.path.dirname(filename):
            filepath = os.path.join(self.output_dir, filename)
        else:
            filepath = filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return filepath


class CustomDataExtractor(DataExtractor):
    """
    Extended DataExtractor that supports custom field configuration
    """
    
    def __init__(self, api_key=None, temp_dir="temp", output_dir="output", fields=None, model_name=None):
        super().__init__(api_key, temp_dir, output_dir, model_name)
        self.fields = fields or ["company_name", "job_title", "apply_link", "salary_range"]
    
    def set_fields(self, fields: List[str]) -> None:
        """Set the fields to extract"""
        self.fields = fields
    
    def generate_beautifulsoup_code(self, html_content, url=None):
        """Override to use custom fields in the prompt"""
        analysis = self.analyze_html_structure(html_content)
        
        # Create field descriptions for the prompt
        field_descriptions = ", ".join(self.fields)
        
        prompt = f"""
You are an expert web scraper. Analyze the following HTML content and generate a Python function using BeautifulSoup that extracts structured data.

HTML Content 
{html_content}

Requirements:
1. Create a function named 'extract_data(html_content)' that takes HTML string as input
2. Return structured data as a JSON-serializable dictionary/list
3. Only extract the following fields: {field_descriptions}
4. Handle edge cases and missing elements gracefully
5. Use descriptive field names in the output that match the requested fields
6. Group related data logically
7. Always return the same structure even if some fields are empty
8. Include error handling
9. For each item/record, include all requested fields even if some are null/empty

The function should follow this template:
```python
from bs4 import BeautifulSoup
import re
from datetime import datetime

def extract_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    extracted_data = []
    
    try:
        # Your extraction logic here
        # Make sure to extract: {field_descriptions}
        # Return consistent structure with requested fields
        return extracted_data
    except Exception as e:
        print(f"Error extracting data: {{e}}")
        return []
```

Only return the Python code, no explanations.
"""
        
        try:
            self.logger.info(f"Generating BeautifulSoup code for fields: {self.fields}")
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                code = response.text.strip()
                
                # Clean up markdown formatting
                if code.startswith('```python'):
                    code = code[9:]
                elif code.startswith('```'):
                    code = code[3:]
                
                if code.endswith('```'):
                    code = code[:-3]
                
                code = code.strip()
                
                self.logger.info("Successfully generated custom BeautifulSoup code")
                return code
            else:
                raise Exception("No response from Gemini API")
                
        except Exception as e:
            self.logger.error(f"Error generating code with Gemini: {str(e)}")
            raise
    
    def extract_data(self, html_content, url=None):
        """Extract data using the current field configuration"""
        try:
            # Generate code with current fields
            extraction_code = self.generate_beautifulsoup_code(html_content, url)
            
            # Execute the code
            extracted_data = self.execute_extraction_code(extraction_code, html_content)
            
            return extracted_data
            
        except Exception as e:
            self.logger.error(f"Data extraction failed: {str(e)}")
            raise


# Convenience function for quick usage
def scrape(url: str, api_key: str, fields: List[str], model_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Quick scraping function for simple use cases.
    
    Args:
        url: URL to scrape
        api_key: Gemini API key
        fields: List of fields to extract
        model_name: Gemini model name (optional, default: 'gemini-2.0-flash-exp')
        
    Returns:
        Extracted data dictionary
    """
    scraper = UniversalScraper(api_key=api_key, model_name=model_name)
    scraper.set_fields(fields)
    return scraper.scrape_url(url)


# Example usage
if __name__ == "__main__":
    # Example of how to use the module
    import os
    
    # Initialize scraper
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Please set GEMINI_API_KEY environment variable")
        exit(1)
    
    # Initialize scraper with custom model (optional)
    scraper = UniversalScraper(api_key=api_key, model_name="gemini-pro")
    
    # Set custom fields
    scraper.set_fields(["company_name", "job_title", "apply_link", "salary_range"])
    
    # Check current model
    print(f"Using model: {scraper.get_model_name()}")
    
    # Scrape a URL
    try:
        result = scraper.scrape_url("https://example.com/jobs", save_to_file=True)
        print(f"Successfully scraped data: {result['metadata']['items_extracted']} items")
        print(f"Fields extracted: {result['fields']}")
        if result.get('saved_to'):
            print(f"Data saved to: {result['saved_to']}")
    except Exception as e:
        print(f"Scraping failed: {e}")