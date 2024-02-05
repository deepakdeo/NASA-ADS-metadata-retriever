# NASA-ADS-metadata-retriever
Retrieves metadata (such as title, url, citation count, pub year, abstract, journal name, bibtex info) of research papers from NASA/ADS webpage (https://ui.adsabs.harvard.edu/) based on matching keywords (in abstract/title/full text) and stores it as a CSV file

This project provides a Python script for retrieving metadata information of research papers from the NASA Astrophysics Data System (ADS) website. It's designed to help researchers, students, and enthusiasts access paper metadata efficiently and programmatically.

## Features

- Retrieve metadata for a list of research papers.
- Parallel processing for faster data retrieval.
- Easy to use and integrate into other projects.

## Output
The output CSV file will contain the following columns:

- **bibcode** - ADS unique identifier for the paper
- **title** - Paper title
- **year** - Publication year
- **pub** - Journal or publication
- **abstract** - Paper abstract
- **keyword** - Author keywords
- **citation_count** - Number of citations
- **BibTeX** - BibTeX entry for citing the paper
- **ADS URL** - Link to the paper details on ADS


## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.6 or higher
- Access to the NASA ADS API and a valid API key. Make an account on https://ui.adsabs.harvard.edu/ then go to settings where you will find 'API Token' from where you can get your own API key.
Note: In a given day you can do a max query of 5000 from API (which is typically more than enough)

## Installation

Clone this repository to your local machine:

```bash
git clone https://github.com/deepakdeo/NASA-ADS-metadata-retriever.git
cd NASA-ADS-metadata-retriever
