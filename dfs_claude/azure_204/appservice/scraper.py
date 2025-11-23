#!/usr/bin/env python3
"""
AZ-204 Microsoft Learn Content Scraper
Extracts all content from Microsoft Learn modules for exam preparation
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import urljoin

BASE_URL = "https://learn.microsoft.com"

# Learning path to scrape
LEARNING_PATH = "/en-us/training/paths/create-azure-app-service-web-apps/"

def get_soup(url):
    """Fetch page and return BeautifulSoup object"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_unit_content(url):
    """Extract educational content from a unit page"""
    full_url = urljoin(BASE_URL, url) if not url.startswith('http') else url
    print(f"    Extracting unit: {full_url}")

    soup = get_soup(full_url)
    if not soup:
        return None

    content = {
        'url': full_url,
        'title': '',
        'content': [],
        'code_examples': [],
        'lists': [],
        'tables': []
    }

    # Get title
    title_elem = soup.find('h1')
    if title_elem:
        content['title'] = title_elem.get_text(strip=True)

    # Find main content area
    main = soup.find('main') or soup.find('article') or soup

    # Extract paragraphs
    for p in main.find_all('p'):
        text = p.get_text(strip=True)
        if text and len(text) > 20:
            content['content'].append(text)

    # Extract headings with their content
    for heading in main.find_all(['h2', 'h3']):
        text = heading.get_text(strip=True)
        if text:
            content['content'].append(f"\n## {text}")

    # Extract code blocks
    for code in main.find_all(['code', 'pre']):
        code_text = code.get_text(strip=True)
        if code_text and len(code_text) > 10:
            content['code_examples'].append(code_text)

    # Extract lists
    for ul in main.find_all(['ul', 'ol']):
        items = [li.get_text(strip=True) for li in ul.find_all('li', recursive=False)]
        if items:
            content['lists'].append(items)

    # Extract tables
    for table in main.find_all('table'):
        rows = []
        for tr in table.find_all('tr'):
            cells = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
            if cells:
                rows.append(cells)
        if rows:
            content['tables'].append(rows)

    time.sleep(0.5)  # Be polite to the server
    return content

def extract_module_units(module_url):
    """Extract all unit URLs from a module page"""
    full_url = urljoin(BASE_URL, module_url) if not module_url.startswith('http') else module_url
    print(f"  Scanning module units: {full_url}")

    soup = get_soup(full_url)
    if not soup:
        return []

    units = []

    # Find unit links in the module's table of contents
    # Units have hrefs like "1-introduction", "2-azure-app-service", etc.
    for link in soup.find_all('a', href=True):
        href = link['href']

        # Match unit URLs pattern: starts with digit followed by dash
        # Can be relative (1-introduction) or absolute path
        if re.match(r'^\d+-', href) or re.search(r'/\d+-[a-z]', href):
            # Resolve relative URL
            unit_url = urljoin(full_url, href)
            unit_url = unit_url.split('?')[0]  # Clean URL

            title = link.get_text(strip=True)
            if unit_url not in [u['url'] for u in units] and title:
                units.append({
                    'url': unit_url,
                    'title': title
                })

    return units

def extract_learning_path_modules(path_url):
    """Extract all modules from the 'Modules in this learning path' section"""
    full_url = urljoin(BASE_URL, path_url) if not path_url.startswith('http') else path_url
    print(f"Scanning learning path: {full_url}")

    soup = get_soup(full_url)
    if not soup:
        return [], ""

    # Get learning path title
    path_title = ""
    title_elem = soup.find('h1')
    if title_elem:
        path_title = title_elem.get_text(strip=True)

    modules = []

    # Find all module cards/links
    # Links can be relative (../../modules/...) or absolute
    for link in soup.find_all('a', href=True):
        href = link['href']

        # Resolve relative URLs first
        resolved_url = urljoin(full_url, href)

        # Check if it's a module URL
        if '/training/modules/' in resolved_url or '/modules/' in href:
            # Clean URL
            if '?' in resolved_url:
                resolved_url = resolved_url.split('?')[0]

            # Ensure it ends with / for consistency
            if not resolved_url.endswith('/'):
                resolved_url += '/'

            # Get title from the link
            title = link.get_text(strip=True)

            # Skip if already added, no title, or too short
            if resolved_url not in [m['url'] for m in modules] and title and len(title) > 5:
                modules.append({
                    'url': resolved_url,
                    'title': title
                })

    # Deduplicate by URL
    seen = set()
    unique_modules = []
    for m in modules:
        if m['url'] not in seen:
            seen.add(m['url'])
            unique_modules.append(m)

    return unique_modules, path_title

def main():
    """Main scraper function"""
    print("=" * 60)
    print("AZ-204 App Service Web Apps Content Scraper")
    print("=" * 60)

    # Extract modules from learning path
    modules, path_title = extract_learning_path_modules(LEARNING_PATH)
    print(f"\nLearning Path: {path_title}")
    print(f"Found {len(modules)} modules\n")

    study_data = {
        'title': path_title or 'Create Azure App Service web apps',
        'url': urljoin(BASE_URL, LEARNING_PATH),
        'extracted_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'modules': []
    }

    for i, module in enumerate(modules, 1):
        print(f"\n[{i}/{len(modules)}] Module: {module['title']}")
        print("-" * 50)

        module_data = {
            'title': module['title'],
            'url': module['url'],
            'topics': []
        }

        # Get all units (topics) in this module
        units = extract_module_units(module['url'])
        print(f"  Found {len(units)} topics")

        for unit in units:
            # Extract content from each unit
            unit_content = extract_unit_content(unit['url'])
            if unit_content:
                topic_data = {
                    'title': unit_content['title'] or unit['title'],
                    'url': unit_content['url'],
                    'content': unit_content['content'],
                    'code_examples': unit_content['code_examples'],
                    'lists': unit_content['lists'],
                    'tables': unit_content['tables']
                }
                module_data['topics'].append(topic_data)

        study_data['modules'].append(module_data)

    # Save to study-data.json
    output_file = 'study-data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(study_data, f, indent=2, ensure_ascii=False)

    # Print summary
    print(f"\n{'=' * 60}")
    print(f"Content saved to {output_file}")
    print(f"Total modules: {len(study_data['modules'])}")
    total_topics = sum(len(m['topics']) for m in study_data['modules'])
    print(f"Total topics: {total_topics}")
    print("=" * 60)

    # Print structure for verification
    print("\nStructure:")
    for module in study_data['modules']:
        print(f"\n📁 {module['title']}")
        for topic in module['topics']:
            print(f"   📄 {topic['title']}")

if __name__ == '__main__':
    main()
