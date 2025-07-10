from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import time
import pandas as pd
import csv
import argparse

def setup_driver():
    """Setup Chrome driver in headless mode."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)

def debug_page_structure(driver):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    print("=== Page Debug Info ===")
    print(f"Page title: {soup.title.string if soup.title else 'No title'}")
    forms = soup.find_all("form")
    print(f"Found {len(forms)} forms")
    for i, form in enumerate(forms):
        print(f"\nForm {i}:")
        print(f"  Action: {form.get('action', 'No action')}")
        print(f"  Method: {form.get('method', 'No method')}")
        selects = form.find_all("select")
        for j, select in enumerate(selects):
            print(f"  Select {j}: name='{select.get('name', 'No name')}', id='{select.get('id', 'No id')}'")
            options = select.find_all("option")
            for k, option in enumerate(options[:5]):
                print(f"    Option {k}: {option.get_text(strip=True)}")
        inputs = form.find_all("input")
        for j, input_elem in enumerate(inputs):
            input_type = input_elem.get("type", "text")
            input_name = input_elem.get("name", "No name")
            input_id = input_elem.get("id", "No id")
            input_value = input_elem.get("value", "")
            print(f"  Input {j}: type='{input_type}', name='{input_name}', id='{input_id}', value='{input_value}'")

def change_results_per_page(driver):
    """Change the results page to show 100 entries instead of 10."""
    try:
        wait = WebDriverWait(driver, 10)
        print("Changing results per page to 100...")
        
        # Find the dropdown for results per page
        results_dropdown = wait.until(EC.presence_of_element_located((By.ID, "dt-length-0")))
        select = Select(results_dropdown)
        select.select_by_value("100")
        
        # Wait for the page to reload with more results
        print("Waiting for page to reload with 100 results...")
        time.sleep(5)  # Increased wait time
        
        # Wait for the table to update with more entries
        print("Waiting for table to update...")
        wait.until(lambda driver: len(driver.find_elements(By.CSS_SELECTOR, "#tblAbstractSearchResults tbody tr")) > 20)
        
        # Check how many entries are actually loaded
        rows = driver.find_elements(By.CSS_SELECTOR, "#tblAbstractSearchResults tbody tr")
        print(f"Found {len(rows)} entries after changing to 100 per page")
        
        return True
    except Exception as e:
        print(f"Error changing results per page: {e}")
        return False

def search_projects(driver, year, category):
    url = "https://abstracts.societyforscience.org"
    print(f"Navigating to {url}")
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    # debug_page_structure(driver)  # Uncomment for debugging
    try:
        # Category dropdown using ID
        print("Selecting category...")
        category_dropdown = wait.until(EC.presence_of_element_located((By.ID, "Category")))
        select = Select(category_dropdown)
        select.select_by_visible_text(category)
        
        # Uncheck the default "0" year checkbox first
        print("Unchecking default year checkbox...")
        default_year_checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@id='SelectedIsefYears0' and @value='0']")))
        if default_year_checkbox.is_selected():
            driver.execute_script("arguments[0].click();", default_year_checkbox)
        
        # Year checkbox using ID (2024 = SelectedIsefYears2)
        year_id_map = {
            2025: "SelectedIsefYears1",
            2024: "SelectedIsefYears2", 
            2023: "SelectedIsefYears3",
            2022: "SelectedIsefYears4",
            2021: "SelectedIsefYears5",
            2020: "SelectedIsefYears6",
            2019: "SelectedIsefYears7",
            2018: "SelectedIsefYears8",
            2017: "SelectedIsefYears9",
            2016: "SelectedIsefYears10",
            2015: "SelectedIsefYears11",
            2014: "SelectedIsefYears12"
        }
        
        year_checkbox_id = year_id_map.get(year, f"SelectedIsefYears{year}")
        print(f"Selecting year {year} with checkbox ID: {year_checkbox_id}")
        year_checkbox = wait.until(EC.element_to_be_clickable((By.ID, year_checkbox_id)))
        driver.execute_script("arguments[0].click();", year_checkbox)
        
        # Select "Only Winning Abstracts" radio button
        print("Selecting 'Only Winning Abstracts'...")
        winning_abstracts_radio = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@id='IsGetAllAbstracts' and @value='False']")))
        driver.execute_script("arguments[0].click();", winning_abstracts_radio)
        
        # Search button
        search_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and contains(@value, 'Search')]")))
        print("Scrolling to and clicking search button...")
        driver.execute_script("arguments[0].scrollIntoView(true);", search_button)
        time.sleep(0.5)
        search_button.click()
        print("Waiting for results...")
        time.sleep(3)
        
        # Change results per page to 100
        change_results_per_page(driver)
        
        return True
    except Exception as e:
        print(f"Error during search: {e}")
        return False

def extract_project_links(driver):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    project_links = []
    table_data = []
    
    # Look for the search results table
    table = soup.find("table", id="tblAbstractSearchResults")
    if table:
        rows = table.find("tbody").find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 8:  # Ensure we have enough columns
                # Extract data from table cells
                year = cells[0].get_text(strip=True)
                finalist_names = cells[1].get_text(strip=True)
                project_title = cells[2].get_text(strip=True)
                category = cells[3].get_text(strip=True)
                fair_country = cells[4].get_text(strip=True)
                fair_state = cells[5].get_text(strip=True)
                fair_province = cells[6].get_text(strip=True)
                awards_won = cells[7].get_text(strip=True)
                
                # Find the project link in the title cell
                link_elem = cells[2].find("a")
                if link_elem:
                    href = link_elem.get("href")
                    if href:
                        if not href.startswith("http"):
                            href = "https://abstracts.societyforscience.org" + href
                        
                        project_links.append(link_elem)
                        table_data.append({
                            "Year": year,
                            "Finalist Names": finalist_names,
                            "Project Title": project_title,
                            "Category": category,
                            "Fair Country": fair_country,
                            "Fair State": fair_state,
                            "Fair Province": fair_province,
                            "Awards Won": awards_won,
                            "href": href
                        })
    
    if not project_links:
        print("No project links found. Page structure:")
        print(f"Page title: {soup.title.string if soup.title else 'No title'}")
        all_links = soup.find_all("a")
        print(f"Total links on page: {len(all_links)}")
        for i, link in enumerate(all_links[:10]):
            href = link.get("href", "")
            text = link.get_text(strip=True)[:50]
            print(f"  Link {i}: {text}... (href: {href})")
    
    return project_links, table_data

def scrape_project_details(driver, project_url):
    driver.get(project_url)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    project_data = {
        "Title": "",
        "Category": "",
        "Year": "",
        "Finalist Names": "",
        "Fair Country": "",
        "Fair State": "",
        "Fair Province": "",
        "Awards Won": "",
        "Abstract": "",
        "Booth Id": ""
    }
    
    # Look for the main content container
    content_div = soup.find("div", class_="col-sm-12")
    if not content_div:
        print("Could not find content div with class 'col-sm-12'")
        return project_data
    
    # Extract title from h2 tag
    title_elem = content_div.find("h2")
    if title_elem:
        project_data["Title"] = title_elem.get_text(strip=True)
    
    # Extract information from p tags
    paragraphs = content_div.find_all("p")
    for p in paragraphs:
        text = p.get_text(strip=True)
        if not text:
            continue
            
        # Extract Booth Id
        if "Booth Id:" in text:
            booth_id = text.replace("Booth Id:", "").strip()
            project_data["Booth Id"] = booth_id
            
        # Extract Category
        elif "Category:" in text:
            category = text.replace("Category:", "").strip()
            project_data["Category"] = category
            
        # Extract Year
        elif "Year:" in text:
            year = text.replace("Year:", "").strip()
            project_data["Year"] = year
            
        # Extract Finalist Names
        elif "Finalist Names:" in text:
            # Handle multi-line names
            names_text = p.get_text()
            names_start = names_text.find("Finalist Names:") + len("Finalist Names:")
            names = names_text[names_start:].strip()
            # Clean up line breaks and extra whitespace
            names = " ".join(names.split())
            project_data["Finalist Names"] = names
            
        # Extract Abstract
        elif "Abstract:" in text:
            # Handle multi-line abstract
            abstract_text = p.get_text()
            abstract_start = abstract_text.find("Abstract:") + len("Abstract:")
            abstract = abstract_text[abstract_start:].strip()
            # Clean up line breaks and extra whitespace
            abstract = " ".join(abstract.split())
            project_data["Abstract"] = abstract
    
    # Try to find project ID from URL
    import re
    project_id_match = re.search(r'projectId=(\d+)', project_url)
    if project_id_match:
        project_data["Project ID"] = project_id_match.group(1)
    
    return project_data

def main():
    parser = argparse.ArgumentParser(description="Scrape ISEF abstracts by year and category")
    parser.add_argument("--year", type=int, default=2024, help="ISEF year (e.g., 2024)")
    parser.add_argument("--category", type=str, default="Physics and Astronomy", help="ISEF category (e.g., 'Physics and Astronomy')")
    args = parser.parse_args()
    driver = setup_driver()
    try:
        year = args.year
        category = args.category
        print(f"Searching for ISEF {year} projects in category: {category}")
        if not search_projects(driver, year, category):
            print("Failed to perform search")
            return
        project_links, table_data = extract_project_links(driver)
        if not project_links:
            print("No project links found")
            return
        print(f"Found {len(project_links)} project links")
        projects_data = []
        for i, (link, table_row) in enumerate(zip(project_links, table_data)):  # Scrape all projects
            href = table_row["href"]
            print(f"Scraping project {i+1}/{len(project_links)}: {href}")
            try:
                project_data = scrape_project_details(driver, href)
                # Merge table data with scraped data
                project_data.update({
                    "Fair Country": table_row["Fair Country"],
                    "Fair State": table_row["Fair State"],
                    "Fair Province": table_row["Fair Province"],
                    "Awards Won": table_row["Awards Won"]
                })
                projects_data.append(project_data)
            except Exception as e:
                print(f"Error scraping project: {e}")
        if projects_data:
            df = pd.DataFrame(projects_data)
            # Reorder columns to match requested sequence
            column_order = [
                "Year", "Finalist Names", "Title", "Category", 
                "Fair Country", "Fair State", "Fair Province", 
                "Awards Won", "Abstract", "Booth Id", "Project ID"
            ]
            df = df[column_order]
            filename = f"isef_{year}_{category.replace(' ', '_').lower()}.csv"
            df.to_csv(filename, index=False)
            print(f"Saved {len(projects_data)} projects to {filename}")
            print(df.head())
        else:
            print("No project data extracted")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
