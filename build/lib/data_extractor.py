import json
import logging
import os
import tempfile
import sys
from datetime import datetime
from urllib.parse import urlparse
import google.generativeai as genai
from bs4 import BeautifulSoup

class DataExtractor:
    def __init__(self, api_key=None, temp_dir="temp", output_dir="output", model_name=None):
        self.logger = logging.getLogger(__name__)
        self.temp_dir = temp_dir
        self.output_dir = output_dir
        self.extraction_codes_dir = os.path.join(temp_dir, "extraction_codes")
        
        # Create directories
        os.makedirs(self.extraction_codes_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Configure Gemini API
        if api_key:
            genai.configure(api_key=api_key)
        else:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("Gemini API key not provided. Set GEMINI_API_KEY environment variable or pass api_key parameter.")
            genai.configure(api_key=api_key)
        
        # Set model name with default fallback
        self.model_name = model_name or 'gemini-2.5-flash'
        self.model = genai.GenerativeModel(self.model_name)
        self.extraction_history = []
        self.logger.info(f"Initialized DataExtractor with model: {self.model_name}")
    
    def analyze_html_structure(self, html_content):
        """Analyze HTML to understand the data structure"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Get basic info about the page
        title = soup.find('title')
        title_text = title.get_text() if title else "No title"
        
        # Count different types of elements
        common_elements = ['div', 'span', 'p', 'a', 'img', 'ul', 'li', 'table', 'tr', 'td']
        element_counts = {}
        for element in common_elements:
            count = len(soup.find_all(element))
            if count > 0:
                element_counts[element] = count
        
        # Look for common patterns that might indicate data
        potential_data_patterns = []
        
        # Check for lists
        lists = soup.find_all(['ul', 'ol'])
        if lists:
            potential_data_patterns.append(f"Found {len(lists)} lists")
        
        # Check for tables
        tables = soup.find_all('table')
        if tables:
            potential_data_patterns.append(f"Found {len(tables)} tables")
        
        # Check for cards/items (common class patterns)
        card_patterns = ['card', 'item', 'post', 'product', 'job', 'listing', 'entry']
        for pattern in card_patterns:
            elements = soup.find_all(class_=lambda x: x and pattern in ' '.join(x).lower())
            if elements:
                potential_data_patterns.append(f"Found {len(elements)} elements with '{pattern}' pattern")
        
        return {
            'title': title_text,
            'element_counts': element_counts,
            'data_patterns': potential_data_patterns,
            'html_length': len(html_content)
        }
    
    def generate_beautifulsoup_code(self, html_content, url=None):
        """Use Gemini to generate BeautifulSoup extraction code"""
        analysis = self.analyze_html_structure(html_content)
        
        # Prepare the prompt for Gemini
        prompt = f"""
You are an expert web scraper. Analyze the following HTML content and generate a Python function using BeautifulSoup that extracts structured data.

HTML Content 
{html_content}

Requirements:
1. Create a function named 'extract_data(html_content)' that takes HTML string as input
2. Return structured data as a JSON-serializable dictionary/list
3. Only extract the company name, apply now link, salary range, job title.
4. Handle edge cases and missing elements gracefully
5. Use descriptive field names in the output
6. Group related data logically
7. Always return the same structure even if some fields are empty
8. Include error handling

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
        # Return consistent structure
        return extracted_data
    except Exception as e:
        print(f"Error extracting data: {{e}}")
        return []
```

Only return the Python code, no explanations.
"""
        
        try:
            self.logger.info("Generating BeautifulSoup code with Gemini...")
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                # Extract Python code from the response
                code = response.text.strip()
                
                # Remove markdown code block markers if present
                if code.startswith('```python'):
                    code = code[9:]
                elif code.startswith('```'):
                    code = code[3:]
                
                if code.endswith('```'):
                    code = code[:-3]
                
                code = code.strip()
                
                self.logger.info("Successfully generated BeautifulSoup code")
                return code
            else:
                raise Exception("No response from Gemini API")
                
        except Exception as e:
            self.logger.error(f"Error generating code with Gemini: {str(e)}")
            raise
    
    def execute_extraction_code(self, code, html_content):
        """Safely execute the generated BeautifulSoup code"""
        try:
            # Create a temporary namespace for execution
            namespace = {
                'BeautifulSoup': BeautifulSoup,
                're': __import__('re'),
                'datetime': __import__('datetime'),
                'json': __import__('json'),
                'print': print
            }
            
            # Execute the code in the namespace
            exec(code, namespace)
            
            # Call the extract_data function
            if 'extract_data' not in namespace:
                raise Exception("Generated code doesn't contain 'extract_data' function")
            
            self.logger.info("Executing generated extraction code...")
            extracted_data = namespace['extract_data'](html_content)
            
            # Validate that the result is JSON serializable
            json.dumps(extracted_data)
            
            self.logger.info(f"Successfully extracted data with {len(extracted_data) if isinstance(extracted_data, list) else 'structured'} items")
            return extracted_data
            
        except Exception as e:
            self.logger.error(f"Error executing extraction code: {str(e)}")
            raise
    
    def _save_extraction_code(self, url, code):
        """Save generated extraction code to temp folder"""
        try:
            if url:
                parsed_url = urlparse(url)
                domain = parsed_url.netloc.replace('www.', '').replace('.', '_')
            else:
                domain = "unknown"
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{domain}_{timestamp}_extraction_code.py"
            filepath = os.path.join(self.extraction_codes_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# Generated extraction code for: {url or 'Unknown URL'}\n")
                f.write(f"# Generated at: {datetime.now().isoformat()}\n\n")
                f.write(code)
            
            self.logger.debug(f"Extraction code saved to: {filepath}")
            return filepath
        except Exception as e:
            self.logger.warning(f"Failed to save extraction code: {e}")
            return None

    def save_data(self, data, filename=None, url=None):
        """Save extracted data to a JSON file in the output directory"""
        if not filename:
            if url:
                parsed_url = urlparse(url)
                domain = parsed_url.netloc.replace('www.', '').replace('.', '_')
            else:
                domain = "unknown"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{domain}_{timestamp}.json"
        
        # Ensure filename goes to output directory
        if not os.path.dirname(filename):
            filepath = os.path.join(self.output_dir, filename)
        else:
            filepath = filename
        
        # Prepare the data with metadata
        output_data = {
            'extraction_info': {
                'timestamp': datetime.now().isoformat(),
                'url': url,
                'total_items': len(data) if isinstance(data, list) else 1
            },
            'data': data
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Data saved to: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error saving data to {filepath}: {str(e)}")
            raise
    
    def extract_and_save(self, html_content, url=None, output_file=None):
        """
        Main method to extract data from HTML and save to file
        """
        try:
            self.logger.info("Starting data extraction process...")
            
            # Generate BeautifulSoup code using Gemini
            extraction_code = self.generate_beautifulsoup_code(html_content, url)
            
            # Store the generated code for debugging
            code_info = {
                'url': url,
                'timestamp': datetime.now().isoformat(),
                'code': extraction_code
            }
            self.extraction_history.append(code_info)
            
            # Execute the generated code
            extracted_data = self.execute_extraction_code(extraction_code, html_content)
            
            # Save the data
            output_filename = self.save_data(extracted_data, output_file, url)
            
            # Save the generated code to temp folder
            code_filename = self._save_extraction_code(url, extraction_code)
            
            self.logger.info(f"Extraction completed. Data: {output_filename}, Code: {code_filename}")
            
            return {
                'success': True,
                'data_file': output_filename,
                'code_file': code_filename,
                'extracted_items': len(extracted_data) if isinstance(extracted_data, list) else 1,
                'extraction_code': extraction_code
            }
            
        except Exception as e:
            self.logger.error(f"Data extraction failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'extraction_code': getattr(self, 'last_generated_code', None)
            }