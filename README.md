# ISEF Scraper

A Python web scraper for extracting ISEF (International Science and Engineering Fair) project data from abstracts.societyforscience.org.

## Prerequisites

1. **Install Python** (if not already installed):
   ```bash
   brew install python3
   ```

2. **Install required Python packages**:
   ```bash
   pip3 install selenium beautifulsoup4 pandas
   ```
   If you encounter any missing dependencies, install them using:
   ```bash
   pip3 install [package_name]
   ```

3. **Install Chrome WebDriver** (required for Selenium):
   ```bash
   brew install --cask chromedriver
   ```
   Or download from: https://chromedriver.chromium.org/

## Running the Scraper

1. **Navigate to the scraper directory**:
   ```bash
   cd /path/to/isef_scraper
   ```

2. **Run the scraper with your desired parameters**:
   ```bash
   python3 isefscraper.py --year 2024 --category "Physics and Astronomy"
   ```

## Parameters

- **`--year`**: ISEF year (e.g., 2024, 2023, 2022, etc.)
- **`--category`**: ISEF category name (e.g., "Physics and Astronomy", "Chemistry", "Engineering", etc.)

**Important**: Be very careful with category spelling - it must match exactly as it appears on the ISEF website.

## Output

The scraper will create a CSV file named `isef_[year]_[category].csv` in the same directory with the following columns:
- Year
- Finalist Names
- Title
- Category
- Fair Country
- Fair State
- Fair Province
- Awards Won
- Abstract
- Booth Id
- Project ID

## Limitations and Customization

1. **Entry Limit**: The scraper is currently configured to load 100 entries per page. If you need to scrape more than 100 projects, you'll need to modify the code in the `change_results_per_page()` function.

2. **Abstract Type**: The scraper is hardcoded to only scrape "Only Winning Abstracts". To scrape all abstracts, modify line 95 in `isefscraper.py`:
   ```python
   # Change from:
   winning_abstracts_radio = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@id='IsGetAllAbstracts' and @value='False']")))
   
   # To:
   winning_abstracts_radio = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@id='IsGetAllAbstracts' and @value='True']")))
   ```

## Troubleshooting

- If you get "ModuleNotFoundError", make sure you've installed all required packages with pip3
- If Chrome WebDriver fails, ensure chromedriver is installed and in your PATH
- If no results are found, double-check the category spelling and year
- The scraper runs in headless mode by default - if you need to see the browser, modify the `setup_driver()` function

## Example Usage

```bash
# Scrape 2024 Physics and Astronomy projects
python3 isefscraper.py --year 2024 --category "Physics and Astronomy"

# Scrape 2023 Chemistry projects
python3 isefscraper.py --year 2023 --category "Chemistry"

# Scrape 2022 Engineering projects
python3 isefscraper.py --year 2022 --category "Engineering"
```

## Features

- Automated form interaction to select year, category, and abstract type
- Extracts comprehensive project data including titles, abstracts, awards, and participant information
- Handles dynamic content loading with proper waits
- Saves results to CSV format with organized column structure
- Supports multiple years and categories
- Headless browser operation for efficient scraping

## Dependencies

- selenium: Web automation and browser control
- beautifulsoup4: HTML parsing and data extraction
- pandas: Data manipulation and CSV export
- Chrome WebDriver: Browser automation driver 