import logging
import os
from datetime import datetime
from urllib.parse import urlparse
from bs4 import BeautifulSoup, Comment
import re
from collections import Counter
from difflib import SequenceMatcher

class HtmlCleaner:
    def __init__(self, temp_dir="temp"):
        self.logger = logging.getLogger(__name__)
        self.temp_dir = temp_dir
        self.cleaned_html_dir = os.path.join(temp_dir, "cleaned_html")
        os.makedirs(self.cleaned_html_dir, exist_ok=True)
        
        self.header_tags = ['header', 'nav', 'aside']
        self.footer_tags = ['footer']
        self.noise_tags = ['script', 'style', 'meta', 'link', 'noscript']
        
    def remove_noise(self, soup):
        """Remove script tags, styles, comments and other noise"""
        # Remove script and style elements
        for tag_name in self.noise_tags:
            for element in soup.find_all(tag_name):
                element.decompose()
        
        # Remove HTML comments
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
        
        return soup
    
    def remove_header_footer(self, soup):
        """Remove header and footer elements"""
        # Remove by semantic tags
        for tag_name in self.header_tags + self.footer_tags:
            for element in soup.find_all(tag_name):
                element.decompose()
        
        # Remove by common class/id patterns
        header_patterns = ['header', 'nav', 'navigation', 'menu', 'top-bar', 'masthead']
        footer_patterns = ['footer', 'bottom', 'copyright', 'legal']
        
        for pattern in header_patterns + footer_patterns:
            # Remove by class
            for element in soup.find_all(class_=re.compile(pattern, re.I)):
                element.decompose()
            # Remove by id
            for element in soup.find_all(id=re.compile(pattern, re.I)):
                element.decompose()
        
        return soup
    
    def get_element_signature(self, element):
        """Generate a signature for an element based on its structure"""
        if not element.name:
            return None
            
        # Create signature from tag structure, classes, and attribute patterns
        signature_parts = []
        
        # Tag name
        signature_parts.append(element.name)
        
        # Classes (sorted for consistency)
        if element.get('class'):
            classes = sorted(element.get('class'))
            signature_parts.append('classes:' + ','.join(classes))
        
        # Important attributes (excluding unique identifiers)
        important_attrs = ['role', 'type', 'data-*']
        for attr in element.attrs:
            if attr in important_attrs or attr.startswith('data-'):
                signature_parts.append(f"{attr}:{element.attrs[attr]}")
        
        # Child element structure (first level only)
        child_tags = []
        for child in element.children:
            if hasattr(child, 'name') and child.name:
                child_tags.append(child.name)
        if child_tags:
            signature_parts.append('children:' + ','.join(sorted(set(child_tags))))
        
        return '|'.join(signature_parts)
    
    def find_similar_elements(self, soup, similarity_threshold=0.8, min_occurrences=3):
        """Find elements with similar structure that might be duplicates"""
        body = soup.find('body')
        if not body:
            return []
        
        # Get all elements that could be potential duplicates
        potential_containers = body.find_all(['div', 'article', 'section', 'li', 'tr'])
        
        # Generate signatures for all elements
        signatures = {}
        element_map = {}
        
        for element in potential_containers:
            # Skip if element is too small or too nested
            if len(str(element)) < 100:
                continue
            
            signature = self.get_element_signature(element)
            if not signature:
                continue
                
            if signature not in signatures:
                signatures[signature] = []
                element_map[signature] = []
            
            signatures[signature].append(element)
            element_map[signature].append(element)
        
        # Find signatures that appear multiple times
        duplicate_groups = []
        for signature, elements in signatures.items():
            if len(elements) >= min_occurrences:
                # Additional similarity check using text content structure
                text_signatures = []
                for elem in elements:
                    text = elem.get_text(strip=True)
                    # Create a pattern from text structure (word count, numbers, etc.)
                    words = len(text.split())
                    numbers = len(re.findall(r'\d+', text))
                    text_signatures.append(f"words:{words},numbers:{numbers}")
                
                # Group by similar text signatures
                text_counter = Counter(text_signatures)
                most_common_text_sig = text_counter.most_common(1)[0]
                
                if most_common_text_sig[1] >= min_occurrences:
                    duplicate_groups.append(elements)
        
        return duplicate_groups

    def focus_on_main_content(self, soup):
        """Try to identify and focus on the main content area"""
        main_content_selectors = [
            'main', '[role="main"]', '#main', '.main',
            '#content', '.content', '#main-content', '.main-content',
            'article', '.article', '#article',
            '.container .content', '.page-content'
        ]
        
        for selector in main_content_selectors:
            try:
                main_element = soup.select_one(selector)
                if main_element and len(main_element.get_text(strip=True)) > 500:
                    self.logger.info(f"Found main content using selector: {selector}")
                    # Create new soup with just the main content
                    new_soup = BeautifulSoup(str(main_element), 'html.parser')
                    return new_soup
            except:
                continue
        
        # If no main content found, return body content
        body = soup.find('body')
        if body:
            return BeautifulSoup(str(body), 'html.parser')
        
        return soup
    
    def remove_empty_divs_recursive(self, soup):
        """Recursively remove empty div elements starting from innermost"""
        def has_meaningful_content(element):
            """Check if an element has meaningful text content"""
            if not element:
                return False
            
            # Get text content and strip whitespace
            text = element.get_text(strip=True)
            if text:
                return True
            
            # Check for meaningful attributes that indicate the div serves a purpose
            # (like images, inputs, or other interactive elements)
            meaningful_tags = ['img', 'input', 'button', 'a', 'form', 'iframe', 'video', 'audio', 'canvas', 'svg']
            for tag in meaningful_tags:
                if element.find(tag):
                    return True
            
            # Check for data attributes or specific classes that might indicate functionality
            if element.get('data-') or element.get('id'):
                # Be more selective - only keep if it seems functional
                attrs = element.attrs
                for attr_name in attrs:
                    if attr_name.startswith('data-') and not attr_name.startswith('data-testid'):
                        return True
                    if attr_name == 'id' and not any(x in str(attrs[attr_name]).lower() for x in ['placeholder', 'skeleton', 'loading']):
                        return True
            
            return False
        
        def remove_empty_divs_pass(soup):
            """Single pass of empty div removal"""
            removed_count = 0
            
            # Find all div elements, starting from deepest nesting
            all_divs = soup.find_all('div')
            
            # Sort by nesting depth (deepest first) to handle innermost divs first
            divs_by_depth = []
            for div in all_divs:
                depth = len(list(div.parents))
                divs_by_depth.append((depth, div))
            
            # Sort by depth in descending order (deepest first)
            divs_by_depth.sort(key=lambda x: x[0], reverse=True)
            
            for depth, div in divs_by_depth:
                if div.parent is None:  # Already removed
                    continue
                
                if not has_meaningful_content(div):
                    # Check if removing this div would break structure
                    parent = div.parent
                    if parent and parent.name in ['html', 'head', 'body']:
                        # Don't remove direct children of important structural elements
                        # unless they're completely empty
                        if not div.get_text(strip=True) and not div.find_all():
                            div.decompose()
                            removed_count += 1
                    else:
                        div.decompose()
                        removed_count += 1
            
            return removed_count
        
        # Keep removing empty divs until no more can be removed
        total_removed = 0
        max_iterations = 10  # Prevent infinite loops
        iteration = 0
        
        while iteration < max_iterations:
            removed_this_pass = remove_empty_divs_pass(soup)
            total_removed += removed_this_pass
            
            if removed_this_pass == 0:
                break  # No more empty divs to remove
                
            iteration += 1
        
        self.logger.info(f"Removed {total_removed} empty div elements in {iteration} iterations")
        return soup
    
    def _save_cleaned_html(self, url, html_content, stage):
        """Save cleaned HTML at different stages to temp folder for debugging"""
        try:
            if url:
                parsed_url = urlparse(url)
                domain = parsed_url.netloc.replace('www.', '').replace('.', '_')
            else:
                domain = "unknown"
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{domain}_{timestamp}_{stage}.html"
            filepath = os.path.join(self.cleaned_html_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.debug(f"Cleaned HTML ({stage}) saved to: {filepath}")
            return filepath
        except Exception as e:
            self.logger.warning(f"Failed to save cleaned HTML: {e}")
            return None

    def clean_html(self, html_content, url=None, save_temp=True):
        """
        Main method to clean HTML content:
        1. Remove noise (scripts, styles, comments)
        2. Remove headers and footers
        3. Focus on main content
        4. Remove empty div elements recursively
        """
        self.logger.info("Starting HTML cleaning process...")
        
        soup = BeautifulSoup(html_content, 'html.parser')
        original_length = len(str(soup))
        
        # Step 1: Remove noise
        soup = self.remove_noise(soup)
        step1_html = str(soup)
        self.logger.info(f"Removed noise. Length: {len(step1_html)}")
        if save_temp:
            self._save_cleaned_html(url, step1_html, "01_removed_noise")
        
        # Step 2: Remove headers and footers
        soup = self.remove_header_footer(soup)
        step2_html = str(soup)
        self.logger.info(f"Removed headers/footers. Length: {len(step2_html)}")
        if save_temp:
            self._save_cleaned_html(url, step2_html, "02_removed_header_footer")
        
        # Step 3: Focus on main content
        soup = self.focus_on_main_content(soup)
        step3_html = str(soup)
        self.logger.info(f"Focused on main content. Length: {len(step3_html)}")
        if save_temp:
            self._save_cleaned_html(url, step3_html, "03_main_content")
        
        # Step 4: Remove empty divs recursively
        soup = self.remove_empty_divs_recursive(soup)
        step4_html = str(soup)
        self.logger.info(f"Removed empty divs. Length: {len(step4_html)}")
        if save_temp:
            self._save_cleaned_html(url, step4_html, "04_removed_empty_divs")
        
        final_html = str(soup)
        final_length = len(final_html)
        if save_temp:
            self._save_cleaned_html(url, final_html, "05_final_cleaned")
        
        self.logger.info(f"HTML cleaning completed. Original: {original_length}, Final: {final_length}")
        self.logger.info(f"Reduction: {((original_length - final_length) / original_length * 100):.1f}%")
        
        return final_html