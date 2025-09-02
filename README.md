<h1 align="center"> Universal Scraper</h1>

<h2 align="center"> The Python package for scraping data from any website</h2>

<p align="center">
<a href="https://pypi.org/project/universal-scraper/"><img alt="pypi" src="https://img.shields.io/pypi/v/universal-scraper.svg"></a>
<a href="https://pepy.tech/project/universal-scraper?versions=1*&versions=2*&versions=3*"><img alt="Downloads" src="https://pepy.tech/badge/universal-scraper/month"></a>
<a href="https://github.com/Ayushi0405/Universal_Scrapper/commits/main"><img alt="GitHub lastest commit" src="https://img.shields.io/github/last-commit/Ayushi0405/Universal_Scrapper?color=blue&style=flat-square"></a>
<a href="#"><img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/universal-scraper?style=flat-square"></a>
</p>

--------------------------------------------------------------------------

A Python module for AI-powered web scraping with customizable field extraction using Google's Gemini AI.

## Features

- 🤖 **AI-Powered Extraction**: Uses Google Gemini to intelligently extract structured data
- 🎯 **Customizable Fields**: Define exactly which fields you want to extract (e.g., company name, job title, salary)
- 🚀 **Smart Caching**: Automatically caches extraction code based on HTML structure - saves 90%+ API tokens on repeat scraping
- 🧹 **Smart HTML Cleaner**: Removes noise and reduces HTML by 65%+ - significantly cuts token usage for AI processing
- 🔧 **Easy to Use**: Simple API for both quick scraping and advanced use cases
- 📦 **Modular Design**: Built with clean, modular components
- 🛡️ **Robust**: Handles edge cases, missing data, and various HTML structures
- 💾 **JSON Output**: Clean, structured JSON output with metadata

## Installation (Recommended)

```
pip install universal-scraper
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Universal_Scrapper
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   Or install manually:
   ```bash
   pip install google-generativeai beautifulsoup4 requests selenium lxml html5lib fake-useragent
   ```

3. **Install the module**:
   ```bash
   pip install -e .
   ```

## Quick Start

### 1. Set up your API key

Get a Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey) and set it as an environment variable:

```bash
export GEMINI_API_KEY="your_gemini_api_key_here"
```

### 2. Basic Usage

```python
from universal_scraper import UniversalScraper

# Initialize the scraper (uses default model: gemini-2.5-flash)
scraper = UniversalScraper(api_key="your_gemini_api_key")

# Or initialize with a custom model
scraper = UniversalScraper(api_key="your_gemini_api_key", model_name="gemini-pro")

# Set the fields you want to extract
scraper.set_fields([
    "company_name", 
    "job_title", 
    "apply_link", 
    "salary_range",
    "location"
])

# Check current model
print(f"Using model: {scraper.get_model_name()}")

# Scrape a URL
result = scraper.scrape_url("https://example.com/jobs", save_to_file=True)

print(f"Extracted {result['metadata']['items_extracted']} items")
print(f"Data saved to: {result.get('saved_to')}")
```

### 3. Convenience Function

For quick one-off scraping:

```python
from universal_scraper import scrape

# Quick scraping with default model
data = scrape(
    url="https://example.com/jobs",
    api_key="your_gemini_api_key",
    fields=["company_name", "job_title", "apply_link"]
)

# Quick scraping with custom model
data = scrape(
    url="https://example.com/jobs",
    api_key="your_gemini_api_key",
    fields=["company_name", "job_title", "apply_link"],
    model_name="gemini-1.5-pro"
)

print(data['data'])  # The extracted data
```

## 🧹 Smart HTML Cleaning

**Reduces HTML size by 65%+** before sending to AI - dramatically cuts token usage:

### What Gets Removed
- **Scripts & Styles**: JavaScript, CSS, and style blocks
- **Ads & Analytics**: Advertisement content and tracking scripts
- **Navigation**: Headers, footers, sidebars, and menu elements  
- **Metadata**: Meta tags, SEO tags, and hidden elements
- **Noise**: Comments, unnecessary attributes, and whitespace

### Benefits
- **Token Reduction**: 65%+ smaller HTML means 65%+ fewer tokens to process
- **Better AI Focus**: Clean HTML helps AI generate more accurate extraction code
- **Faster Processing**: Less data to analyze means faster response times
- **Cost Savings**: Fewer tokens = lower API costs per extraction

### Example Impact
```
Original HTML: 150KB → Cleaned HTML: 45KB (70% reduction)
Before: ~38,000 tokens → After: ~11,000 tokens (saves 27K tokens per request!)
```

## 🚀 Smart Caching (NEW!)

**Saves 90%+ API tokens** by reusing extraction code for similar HTML structures:

### Key Benefits
- **Token Savings**: Avoids regenerating BeautifulSoup code for similar pages
- **Performance**: 5-10x faster scraping on cached structures  
- **Cost Reduction**: Significant API cost savings for repeated scraping
- **Automatic**: Works transparently - no code changes needed

### How It Works
- **Structural Hashing**: Creates hash based on HTML structure (not content)
- **Smart Matching**: Reuses code when URL domain + structure + fields match
- **Local SQLite DB**: Stores cached extraction codes permanently

### Cache Management
```python
scraper = UniversalScraper(api_key="your_key")

# View cache statistics
stats = scraper.get_cache_stats()
print(f"Cached entries: {stats['total_entries']}")
print(f"Total cache hits: {stats['total_uses']}")

# Clear old entries (30+ days)
removed = scraper.cleanup_old_cache(30)
print(f"Removed {removed} old entries")

# Clear entire cache
scraper.clear_cache()

# Disable/enable caching
scraper.disable_cache()  # For testing
scraper.enable_cache()   # Re-enable
```

## Advanced Usage

### Multiple URLs

```python
scraper = UniversalScraper(api_key="your_api_key")
scraper.set_fields(["title", "price", "description"])

urls = [
    "https://site1.com/products",
    "https://site2.com/items", 
    "https://site3.com/listings"
]

results = scraper.scrape_multiple_urls(urls, save_to_files=True)

for result in results:
    if result.get('error'):
        print(f"Failed {result['url']}: {result['error']}")
    else:
        print(f"Success {result['url']}: {result['metadata']['items_extracted']} items")
```

### Custom Configuration

```python
scraper = UniversalScraper(
    api_key="your_api_key",
    temp_dir="custom_temp",      # Custom temporary directory
    output_dir="custom_output",  # Custom output directory  
    log_level=logging.DEBUG,     # Enable debug logging
    model_name="gemini-pro"      # Custom Gemini model
)

# Configure for e-commerce scraping
scraper.set_fields([
    "product_name",
    "product_price", 
    "product_rating",
    "product_reviews_count",
    "product_availability",
    "product_description"
])

# Check and change model dynamically
print(f"Current model: {scraper.get_model_name()}")
scraper.set_model_name("gemini-1.5-pro")
print(f"Switched to: {scraper.get_model_name()}")

result = scraper.scrape_url("https://ecommerce-site.com", save_to_file=True)
```

## API Reference

### UniversalScraper Class

#### Constructor
```python
UniversalScraper(api_key=None, temp_dir="temp", output_dir="output", log_level=logging.INFO, model_name=None)
```

- `api_key`: Gemini API key (optional if GEMINI_API_KEY env var is set)
- `temp_dir`: Directory for temporary files
- `output_dir`: Directory for output files
- `log_level`: Logging level
- `model_name`: Gemini model name (default: 'gemini-2.5-flash')

#### Methods

- `set_fields(fields: List[str])`: Set the fields to extract
- `get_fields() -> List[str]`: Get current fields configuration
- `get_model_name() -> str`: Get current Gemini model name
- `set_model_name(model_name: str)`: Change the Gemini model
- `scrape_url(url: str, save_to_file=False, output_filename=None) -> Dict`: Scrape a single URL
- `scrape_multiple_urls(urls: List[str], save_to_files=True) -> List[Dict]`: Scrape multiple URLs

### Convenience Function

```python
scrape(url: str, api_key: str, fields: List[str], model_name: Optional[str] = None) -> Dict
```

Quick scraping function for simple use cases.

## Output Format

The scraped data is returned in a structured format:

```json
{
  "url": "https://example.com",
  "timestamp": "2025-01-01T12:00:00",
  "fields": ["company_name", "job_title", "apply_link"],
  "data": [
    {
      "company_name": "Example Corp",
      "job_title": "Software Engineer", 
      "apply_link": "https://example.com/apply/123"
    }
  ],
  "metadata": {
    "raw_html_length": 50000,
    "cleaned_html_length": 15000,
    "items_extracted": 1
  }
}
```

## Common Field Examples

### Job Listings
```python
scraper.set_fields([
    "company_name",
    "job_title", 
    "apply_link",
    "salary_range",
    "location",
    "job_description",
    "employment_type",
    "experience_level"
])
```

### E-commerce Products
```python
scraper.set_fields([
    "product_name",
    "product_price",
    "product_rating", 
    "product_reviews_count",
    "product_availability",
    "product_image_url",
    "product_description"
])
```

### News Articles
```python
scraper.set_fields([
    "article_title",
    "article_content",
    "article_author",
    "publish_date", 
    "article_url",
    "article_category"
])
```

## Testing

Run the test suite to verify everything works:

```bash
python test_module.py
```

## Example Files

- `example_usage.py`: Comprehensive examples of different usage patterns
- `test_module.py`: Test suite for the module

## How It Works

1. **HTML Fetching**: Uses cloudscraper to fetch HTML content, handling anti-bot measures
2. **Smart HTML Cleaning**: Removes 65%+ of noise (scripts, ads, navigation) while preserving data structure
3. **Structure-Based Caching**: Creates structural hash and checks cache for existing extraction code
4. **AI Code Generation**: Uses Google Gemini to generate custom BeautifulSoup code (only when not cached)
5. **Code Execution**: Runs the cached/generated code to extract structured data
6. **JSON Output**: Returns clean, structured data with metadata and performance stats

## Troubleshooting

### Common Issues

1. **API Key Error**: Make sure your Gemini API key is valid and set correctly
2. **Empty Results**: The AI might need more specific field names or the page might not contain the expected data
3. **Network Errors**: Some sites block scrapers - the tool uses cloudscraper to handle most cases

### Debug Mode

Enable debug logging to see what's happening:

```python
import logging
scraper = UniversalScraper(api_key="your_key", log_level=logging.DEBUG)
```

## Core Contributors

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->

<table>
<tr>

<td align="center">
    <a href="https://github.com/PushpenderIndia">
        <kbd><img src="https://avatars3.githubusercontent.com/PushpenderIndia?size=400" width="100px;" alt=""/></kbd><br />
        <sub><b>Pushpender Singh</b></sub>
    </a><br />
    <a href="https://github.com/Ayushi0405/Universal_Scrapper/commits?author=PushpenderIndia" title="Code"> :computer: </a> 
</td>

<td align="center">
    <a href="https://github.com/Ayushi0405">
        <kbd><img src="https://avatars3.githubusercontent.com/Ayushi0405?size=400" width="100px;" alt=""/></kbd><br />
        <sub><b>Ayushi Gupta</b></sub>
    </a><br />
    <a href="https://github.com/Ayushi0405/Universal_Scrapper/commits?author=Ayushi0405" title="Code"> :computer: </a> 
</td>

</tr>
</tr>
</table>

<!-- markdownlint-enable -->
<!-- prettier-ignore-end -->
<!-- ALL-CONTRIBUTORS-LIST:END -->

Contributions of any kind welcome!

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python test_module.py`
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Changelog

### v1.2.0 - Smart Caching & HTML Optimization Release
- 🚀 **NEW**: Intelligent code caching system - **saves 90%+ API tokens**
- 🧹 **HIGHLIGHT**: Smart HTML cleaner reduces payload by 65%+ - **massive token savings**
- 🔧 **NEW**: Structural HTML hashing for cache key generation
- 🔧 **NEW**: SQLite-based cache storage with metadata
- 🔧 **NEW**: Cache management methods: `get_cache_stats()`, `clear_cache()`, `cleanup_old_cache()`
- 🔧 **NEW**: Automatic cache hit/miss detection and logging  
- 🔧 **NEW**: URL normalization (removes query params) for better cache matching
- ⚡ **PERF**: 5-10x faster scraping on cached HTML structures
- 💰 **COST**: Significant API cost reduction (HTML cleaning + caching combined)
- 📁 **ORG**: Moved sample code to `sample_code/` directory

### v1.1.0
- ✨ **NEW**: Gemini model selection functionality
- 🔧 Added `model_name` parameter to `UniversalScraper()` constructor
- 🔧 Added `get_model_name()` and `set_model_name()` methods
- 🔧 Enhanced convenience `scrape()` function with `model_name` parameter  
- 🔄 Updated default model to `gemini-2.5-flash`
- 📚 Updated documentation with model examples
- ✅ Fixed missing `cloudscraper` dependency

### v1.0.0
- Initial release
- AI-powered field extraction
- Customizable field configuration
- Multiple URL support
- Comprehensive test suite
