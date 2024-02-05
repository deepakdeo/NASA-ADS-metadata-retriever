import requests
import csv
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Constants
BASE_URL = "https://api.adsabs.harvard.edu/v1/search/query?"
EXPORT_URL = "https://api.adsabs.harvard.edu/v1/export/bibtex"
API_KEY = 'xxxx'  # Replace with your actual API key
CSV_FILE_PATH = "NASAads_papers_info_test.csv"  # Update this path as needed

# Query Parameters, following is an example use of keywords and other query parameters
QUERY_PARAMS = {
    "q": (
        "("
        "title:\"recently quenched elliptical\" OR title:\"quenched elliptical galax*\""
        " OR "
        "abs:\"recently quenched elliptical\" OR abs:\"quenched elliptical galax*\""
        " OR "
        "full:\"recently quenched elliptical\" OR full:\"quenched elliptical galax*\""
        ") AND "
        "property:refereed AND "
        "database:\"astronomy\" AND "
        "year:[1850 TO 2024]"
    ),
    "fl": "bibcode,title,year,pub,abstract,keyword,citation_count",
    "rows": 100,  # Adjust as needed, it means you are asking the API to return up to 100 papers per request.
    "sort": "date desc"
}


# Function to fetch BibTeX data
def get_bibtex(bibcode):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.post(EXPORT_URL, headers=headers, json={"bibcode": [bibcode]})
    if response.status_code == 200:
        return response.json().get('export', '')
    else:
        print(f"Error getting BibTeX for {bibcode}: {response.status_code}")
        return ''

# Function to get the total count of papers
def get_total_papers():
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.get(BASE_URL, headers=headers, params=QUERY_PARAMS)
    if response.status_code == 200:
        total_papers = response.json().get("response", {}).get("numFound", 0)
        return total_papers
    else:
        print(f"Error fetching total number of papers: {response.status_code}")
        return 0

# Function to query NASA ADS API with pagination
def query_nasa_ads(start, rows=100):
    params = QUERY_PARAMS.copy()
    params["rows"] = rows
    params["start"] = start
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.get(BASE_URL, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json().get("response", {}).get("docs", [])
        return [(paper, get_bibtex(paper['bibcode'])) for paper in data]
    else:
        print(f"Error: {response.status_code}")
        return []


# Main function to get total hits and process papers
def main():
    start_time = time.time()
    total_papers = get_total_papers()
    print(f"Total number of papers available: {total_papers}.\nIt would take approximately {total_papers}s or less to retrieve all info.")

    max_papers = int(input("Enter the number of papers to process (up to the total available): "))
    max_papers = min(max_papers, total_papers)

    papers_info = []
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(query_nasa_ads, start, QUERY_PARAMS["rows"]) for start in
                   range(0, max_papers, QUERY_PARAMS["rows"])]
        for future in as_completed(futures):
            papers_info.extend(future.result())

    # Writing to CSV
    with open(CSV_FILE_PATH, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["bibcode", "title", "year", "pub", "abstract", "keyword", "citation_count", "BibTeX", "ADS URL"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for paper, bibtex in papers_info:
            paper_dict = {field: paper.get(field, '') for field in fieldnames[:-2]}
            paper_dict["BibTeX"] = bibtex
            paper_dict["ADS URL"] = f"https://ui.adsabs.harvard.edu/abs/{paper['bibcode']}/abstract"
            writer.writerow(paper_dict)

    print(f"Paper information has been saved to '{CSV_FILE_PATH}'.")
    print(f"Total execution time: {time.time() - start_time:.2f} seconds")


if __name__ == "__main__":
    main()
