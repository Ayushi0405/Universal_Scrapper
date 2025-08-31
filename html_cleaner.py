#!/usr/bin/env python3
"""
Object-Oriented HTML Cleaner and Deduplicator
A comprehensive HTML cleaning tool using strict OOP principles
"""

import re
import sys
import os
from collections import OrderedDict
from urllib.parse import urlparse
import time
from bs4 import BeautifulSoup, Comment
import hashlib
from abc import ABC, abstractmethod


class CleaningStrategy(ABC):
    """Abstract base class for HTML cleaning strategies"""
    
    @abstractmethod
    def clean(self, soup, stats):
        """Clean HTML soup using this strategy"""
        pass
    
    @property
    @abstractmethod
    def strategy_name(self):
        """Return the name of this cleaning strategy"""
        pass


class CommentRemovalStrategy(CleaningStrategy):
    """Strategy for removing HTML comments"""
    
    @property
    def strategy_name(self):
        return "Comment Removal"
    
    def clean(self, soup, stats):
        """Remove all HTML comments"""
        comments = soup.find_all(string=lambda text: isinstance(text, Comment))
        removed_count = 0                                                                                            
        
        for comment in comments:
            comment.extract()
            removed_count += 1
        
        stats.update_stat('removed_comments', removed_count)
        return soup


class ScriptStyleRemovalStrategy(CleaningStrategy):
    """Strategy for removing script and style tags"""
    
    @property
    def strategy_name(self):
        return "Script and Style Removal"
    
    def clean(self, soup, stats):
        """Remove script and style tags"""
        # Remove script tags
        scripts = soup.find_all('script')
        for script in scripts:
            script.decompose()
            stats.increment_stat('removed_scripts')
        
        # Remove style tags
        styles = soup.find_all('style')
        for style in styles:
            style.decompose()
            stats.increment_stat('removed_styles')
        
        # Remove inline styles
        for element in soup.find_all(style=True):
            del element['style']
        
        return soup


class DuplicateRemovalStrategy(CleaningStrategy):
    """Strategy for removing duplicate HTML elements"""
    
    def __init__(self):
        self.element_signatures = {}
        self.signature_generator = ElementSignatureGenerator()
    
    @property
    def strategy_name(self):
        return "Duplicate Element Removal"
    
    def clean(self, soup, stats):
        """Remove duplicate elements based on content and structure"""
        elements_to_remove = []
        
        # Process all elements
        for element in soup.find_all():
            if element.name in ['html', 'head', 'body']:
                continue  # Skip structural elements
            
            signature = self.signature_generator.generate_signature(element)
            
            if signature in self.element_signatures:
                # This is a duplicate
                elements_to_remove.append(element)
                stats.increment_stat('removed_duplicates')
            else:
                self.element_signatures[signature] = element
        
        # Remove duplicates
        for element in elements_to_remove:
            try:
                element.decompose()
            except:
                pass
        
        return soup


class EmptyElementRemovalStrategy(CleaningStrategy):
    """Strategy for removing empty HTML elements"""
    
    def __init__(self):
        self.empty_tags = ['div', 'span', 'p', 'section', 'article', 'aside']
    
    @property
    def strategy_name(self):
        return "Empty Element Removal"
    
    def clean(self, soup, stats):
        """Remove empty elements that don't contribute to structure"""
        removed_empty = 0
        
        for tag_name in self.empty_tags:
            for element in soup.find_all(tag_name):
                # Check if element is empty or contains only whitespace
                if not element.get_text(strip=True) and not element.find_all():
                    element.decompose()
                    removed_empty += 1
        
        stats.update_stat('removed_empty', removed_empty)
        return soup


class ElementSignatureGenerator:
    """Generates unique signatures for HTML elements"""
    
    def __init__(self):
        self.dynamic_attributes = ['id', 'data-reactid', 'data-test', 'aria-describedby']
    
    def generate_signature(self, element):
        """Generate a signature for an element based on its structure and content"""
        # Create signature from tag name, attributes, and text content
        tag_name = element.name or ''
        
        # Get sorted attributes (excluding dynamic ones)
        attrs = self._get_cleaned_attributes(element)
        attrs_str = str(sorted(attrs.items()))
        
        # Get text content (first 200 chars to avoid very long signatures)
        text_content = element.get_text(strip=True)[:200]
        
        # Get child structure (tag names of immediate children)
        child_structure = self._get_child_structure(element)
        
        # Create hash signature
        signature_data = f"{tag_name}|{attrs_str}|{text_content}|{child_structure}"
        signature = hashlib.md5(signature_data.encode()).hexdigest()
        
        return signature
    
    def _get_cleaned_attributes(self, element):
        """Get element attributes excluding dynamic ones"""
        attrs = {}
        if element.attrs:
            for key, value in element.attrs.items():
                # Skip dynamic attributes
                if key not in self.dynamic_attributes:
                    if isinstance(value, list):
                        attrs[key] = ' '.join(sorted(value))
                    else:
                        attrs[key] = str(value)
        return attrs
    
    def _get_child_structure(self, element):
        """Get the structure of immediate children"""
        child_tags = [child.name for child in element.find_all(recursive=False) if child.name]
        return str(sorted(child_tags))


class CleaningStatistics:
    """Manages cleaning statistics and metrics"""
    
    def __init__(self):
        self.stats = {
            'original_size': 0,
            'cleaned_size': 0,
            'removed_duplicates': 0,
            'removed_scripts': 0,
            'removed_styles': 0,
            'removed_comments': 0,
            'removed_empty': 0
        }
    
    def set_original_size(self, size):
        """Set the original file size"""
        self.stats['original_size'] = size
    
    def set_cleaned_size(self, size):
        """Set the cleaned file size"""
        self.stats['cleaned_size'] = size
    
    def increment_stat(self, stat_name):
        """Increment a statistic by 1"""
        if stat_name in self.stats:
            self.stats[stat_name] += 1
    
    def update_stat(self, stat_name, value):
        """Update a statistic with a specific value"""
        if stat_name in self.stats:
            self.stats[stat_name] = value
    
    def get_stat(self, stat_name):
        """Get a specific statistic"""
        return self.stats.get(stat_name, 0)
    
    def get_all_stats(self):
        """Get all statistics"""
        return self.stats.copy()
    
    def get_reduction_percentage(self):
        """Calculate size reduction percentage"""
        if self.stats['original_size'] > 0:
            return ((self.stats['original_size'] - self.stats['cleaned_size']) / self.stats['original_size'] * 100)
        return 0


class HTMLParser:
    """Handles HTML parsing operations"""
    
    def __init__(self):
        self.parser_type = 'html.parser'
    
    def parse_html(self, html_content):
        """Parse HTML content and return BeautifulSoup object"""
        try:
            soup = BeautifulSoup(html_content, self.parser_type)
            return soup
        except Exception as e:
            raise HTMLParsingError(f"Failed to parse HTML: {str(e)}")
    
    def prettify_html(self, soup):
        """Convert soup back to prettified HTML string"""
        try:
            return soup.prettify()
        except Exception as e:
            raise HTMLParsingError(f"Failed to prettify HTML: {str(e)}")


class HeaderCommentGenerator:
    """Generates header comments for cleaned files"""
    
    def generate_header(self, stats):
        """Generate header comment for cleaned file"""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        all_stats = stats.get_all_stats()
        reduction_percent = stats.get_reduction_percentage()
        
        header = f"""<!-- 
HTML CLEANED AND DEDUPLICATED
Generated: {timestamp}
Original size: {all_stats['original_size']:,} characters
Cleaned size: {all_stats['cleaned_size']:,} characters
Reduction: {reduction_percent:.1f}%
Removed: {all_stats['removed_duplicates']} duplicates, {all_stats['removed_scripts']} scripts, {all_stats['removed_styles']} styles, {all_stats['removed_comments']} comments, {all_stats['removed_empty']} empty elements
-->

"""
        return header


class FileManager:
    """Manages file operations for HTML cleaning"""
    
    def read_html_file(self, file_path):
        """Read HTML content from file"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            raise FileOperationError(f"Failed to read file: {str(e)}")
    
    def write_html_file(self, content, file_path):
        """Write HTML content to file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            raise FileOperationError(f"Failed to write file: {str(e)}")
    
    def generate_output_filename(self, input_file, suffix='_cleaned'):
        """Generate output filename based on input filename"""
        base_name = os.path.splitext(input_file)[0]
        extension = os.path.splitext(input_file)[1]
        return f"{base_name}{suffix}{extension}"


class StructurePatternAnalyzer:
    """Analyzes HTML structure patterns"""
    
    def __init__(self):
        self.patterns = {
            'Navigation': ['nav', 'ul.nav', 'div.navbar'],
            'Content Areas': ['main', 'article', 'section.content'],
            'Sidebars': ['aside', 'div.sidebar'],
            'Headers': ['header', 'div.header'],
            'Footers': ['footer', 'div.footer'],
            'Cards/Items': ['div.card', 'div.item', 'article.post'],
            'Forms': ['form'],
            'Lists': ['ul', 'ol'],
            'Tables': ['table']
        }
    
    def analyze_patterns(self, soup):
        """Analyze HTML structure patterns"""
        structures = {}
        
        for category, selectors in self.patterns.items():
            structures[category] = []
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    structures[category].extend([elem.name for elem in elements[:3]])  # Limit to first 3
        
        return structures


class ElementCounter:
    """Counts HTML elements by type"""
    
    def count_elements(self, soup):
        """Count different types of HTML elements"""
        element_counts = {}
        for element in soup.find_all():
            tag = element.name
            element_counts[tag] = element_counts.get(tag, 0) + 1
        
        return element_counts


class StructureAnalyzer:
    """Main class for HTML structure analysis"""
    
    def __init__(self):
        self.pattern_analyzer = StructurePatternAnalyzer()
        self.element_counter = ElementCounter()
        self.file_manager = FileManager()
    
    def analyze_html_structure(self, html_file):
        """Analyze HTML structure and create a summary"""
        try:
            # Read and parse HTML
            html_content = self.file_manager.read_html_file(html_file)
            parser = HTMLParser()
            soup = parser.parse_html(html_content)
            
            # Count elements and analyze patterns
            element_counts = self.element_counter.count_elements(soup)
            unique_structures = self.pattern_analyzer.analyze_patterns(soup)
            
            # Create structure summary
            summary_file = self.file_manager.generate_output_filename(html_file, '_structure.txt')
            self._create_structure_summary(element_counts, unique_structures, summary_file)
            
            return True
            
        except Exception as e:
            raise StructureAnalysisError(f"Failed to analyze structure: {str(e)}")
    
    def _create_structure_summary(self, element_counts, unique_structures, output_file):
        """Create HTML structure summary file"""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"HTML STRUCTURE ANALYSIS\n")
                f.write(f"Generated: {timestamp}\n")
                f.write("="*50 + "\n\n")
                
                f.write("ELEMENT COUNTS:\n")
                f.write("-" * 20 + "\n")
                for tag, count in sorted(element_counts.items()):
                    f.write(f"{tag}: {count}\n")
                
                f.write(f"\nUNIQUE STRUCTURES FOUND:\n")
                f.write("-" * 30 + "\n")
                for category, elements in unique_structures.items():
                    if elements:
                        f.write(f"{category}: {', '.join(set(elements))}\n")
            
            print(f"Structure analysis saved to: {output_file}")
            
        except Exception as e:
            raise FileOperationError(f"Failed to write structure summary: {str(e)}")


class HTMLCleaningEngine:
    """Main HTML cleaning engine that coordinates all cleaning strategies"""
    
    def __init__(self):
        self.strategies = [
            CommentRemovalStrategy(),
            ScriptStyleRemovalStrategy(),
            DuplicateRemovalStrategy(),
            EmptyElementRemovalStrategy()
        ]
        self.parser = HTMLParser()
        self.header_generator = HeaderCommentGenerator()
    
    def clean_html_content(self, html_content, stats):
        """Clean HTML content using all strategies"""
        try:
            # Parse HTML
            soup = self.parser.parse_html(html_content)
            
            # Apply all cleaning strategies
            for strategy in self.strategies:
                print(f"Applying {strategy.strategy_name}...")
                soup = strategy.clean(soup, stats)
            
            # Generate cleaned HTML
            cleaned_html = self.parser.prettify_html(soup)
            
            # Add header comment
            header = self.header_generator.generate_header(stats)
            cleaned_html = header + cleaned_html
            
            return cleaned_html
            
        except Exception as e:
            raise HTMLCleaningError(f"Failed to clean HTML content: {str(e)}")


class HTMLCleaner:
    """Main HTML cleaner class that orchestrates the cleaning process"""
    
    def __init__(self):
        self.file_manager = FileManager()
        self.cleaning_engine = HTMLCleaningEngine()
        self.stats = CleaningStatistics()
    
    def clean_html_file(self, input_file, output_file=None):
        """Clean HTML file and remove duplicates"""
        try:
            print(f"Reading HTML file: {input_file}")
            
            # Read HTML content
            html_content = self.file_manager.read_html_file(input_file)
            self.stats.set_original_size(len(html_content))
            print(f"Original file size: {self.stats.get_stat('original_size'):,} characters")
            
            # Clean the HTML
            cleaned_html = self.cleaning_engine.clean_html_content(html_content, self.stats)
            
            # Generate output filename if not provided
            if not output_file:
                output_file = self.file_manager.generate_output_filename(input_file)
            
            # Save cleaned HTML
            self.file_manager.write_html_file(cleaned_html, output_file)
            
            # Update statistics
            self.stats.set_cleaned_size(len(cleaned_html))
            self._print_cleaning_results(output_file)
            
            return True
            
        except Exception as e:
            print(f"Error cleaning HTML file: {str(e)}")
            return False
    
    def _print_cleaning_results(self, output_file):
        """Print cleaning results and statistics"""
        all_stats = self.stats.get_all_stats()
        reduction_percent = self.stats.get_reduction_percentage()
        
        print("\n" + "="*60)
        print(" HTML CLEANING COMPLETED SUCCESSFULLY")
        print("="*60)
        print(f"Original size: {all_stats['original_size']:,} characters")
        print(f"Cleaned size:  {all_stats['cleaned_size']:,} characters")
        print(f"Size reduction: {reduction_percent:.1f}%")
        print(f"Removed duplicates: {all_stats['removed_duplicates']}")
        print(f"Removed scripts: {all_stats['removed_scripts']}")
        print(f"Removed styles: {all_stats['removed_styles']}")
        print(f"Removed comments: {all_stats['removed_comments']}")
        print(f"Removed empty elements: {all_stats['removed_empty']}")
        print(f"Output file: {output_file}")
        print("="*60)


class ArgumentParser:
    """Parses command line arguments"""
    
    def parse_arguments(self, args):
        """Parse command line arguments"""
        if len(args) < 2:
            return None, None, False
        
        input_file = args[1]
        output_file = None
        analyze_structure = False
        
        i = 2
        while i < len(args):
            arg = args[i]
            if arg in ['--output', '-o']:
                if i + 1 < len(args):
                    output_file = args[i + 1]
                    i += 1
            elif arg in ['--analyze', '-a']:
                analyze_structure = True
            elif not arg.startswith('-'):
                output_file = arg
            i += 1
        
        return input_file, output_file, analyze_structure


class UsageDisplayer:
    """Displays usage instructions"""
    
    def show_usage(self):
        """Show usage instructions"""
        print("  HTML CLEANER AND DEDUPLICATOR")
        print("=" * 40)
        print(" Clean HTML files by removing duplicates and unnecessary content")
        print("")
        print("USAGE:")
        print("  python html_cleaner.py <input_file.html> [options]")
        print("")
        print("EXAMPLES:")
        print("  python html_cleaner.py scraped_page.html")
        print("  python html_cleaner.py data.html --output clean_data.html")
        print("  python html_cleaner.py file.html --analyze")
        print("")
        print("OPTIONS:")
        print("  --output, -o <file>    Specify output filename")
        print("  --analyze, -a          Also create structure analysis")
        print("")
        print("WHAT IT DOES:")
        print("   Removes duplicate HTML elements")
        print("   Removes all JavaScript and CSS")
        print("   Removes HTML comments")
        print("   Removes empty elements")
        print("   Creates clean, readable HTML structure")
        print("   Generates statistics on cleaning")
        print("")
        print(" OUTPUT: Cleaned HTML file with '_cleaned' suffix")


class CommandLineInterface:
    """Command line interface for HTML cleaner"""
    
    def __init__(self):
        self.cleaner = HTMLCleaner()
        self.analyzer = StructureAnalyzer()
        self.argument_parser = ArgumentParser()
        self.usage_displayer = UsageDisplayer()
    
    def run(self, args):
        """Main execution method"""
        try:
            parsed_args = self.argument_parser.parse_arguments(args)
            if not parsed_args[0]:
                self.usage_displayer.show_usage()
                return 1
            
            input_file, output_file, analyze_structure = parsed_args
            
            self._display_execution_info(input_file, output_file, analyze_structure)
            
            # Clean the HTML file
            success = self.cleaner.clean_html_file(input_file, output_file)
            
            if not success:
                return 1
            
            # Analyze structure if requested
            if analyze_structure:
                print("\nAnalyzing HTML structure...")
                final_output_file = output_file or self.cleaner.file_manager.generate_output_filename(input_file)
                self.analyzer.analyze_html_structure(final_output_file)
            
            return 0
            
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return 1
    
    def _display_execution_info(self, input_file, output_file, analyze_structure):
        """Display execution information"""
        print(" HTML CLEANER ACTIVATED!")
        print("=" * 30)
        print(f" Input file: {input_file}")
        if output_file:
            print(f" Output file: {output_file}")
        if analyze_structure:
            print(" Structure analysis: Enabled")
        print("")


# Custom Exception Classes
class HTMLCleaningError(Exception):
    """Exception raised during HTML cleaning operations"""
    pass


class HTMLParsingError(Exception):
    """Exception raised during HTML parsing operations"""
    pass


class FileOperationError(Exception):
    """Exception raised during file operations"""
    pass


class StructureAnalysisError(Exception):
    """Exception raised during structure analysis"""
    pass


def main():
    """Entry point"""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("Error: BeautifulSoup4 is required for HTML parsing")
        print("Install it with: pip install beautifulsoup4")
        sys.exit(1)
    
    cli = CommandLineInterface()
    exit_code = cli.run(sys.argv)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()