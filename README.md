# Universal Scraper Python Module

A Python module for AI-powered web scraping with customizable field extraction using Google's Gemini AI.

## Features

- 🤖 **AI-Powered Extraction**: Uses Google Gemini to intelligently extract structured data
- 🎯 **Customizable Fields**: Define exactly which fields you want to extract (e.g., company name, job title, salary)
- 🔧 **Easy to Use**: Simple API for both quick scraping and advanced use cases
- 📦 **Modular Design**: Built with clean, modular components
- 🛡️ **Robust**: Handles edge cases, missing data, and various HTML structures
- 💾 **JSON Output**: Clean, structured JSON output with metadata

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
2. **HTML Cleaning**: Removes noise, ads, and unnecessary elements while preserving structure
3. **AI Extraction**: Uses Google Gemini to generate custom BeautifulSoup code for your specific fields
4. **Data Processing**: Executes the generated code to extract structured data
5. **Output**: Returns clean JSON data with metadata

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
