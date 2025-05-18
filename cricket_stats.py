import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# ✅ Updated URL with correct class and valid span parameters
def fetch_data():
    url = "https://stats.espncricinfo.com/ci/engine/stats/index.html?class=1;spanmax1=31+Dec+2024;spanmin1=01+Jan+2000;spanval1=span;template=results;type=batting"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/114.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

# ✅ Extract table with duplicate/empty column handling
def extract_table_data(soup):
    tables = soup.find_all('table', {'class': 'engineTable'})

    target_table = None
    for table in tables:
        headers = [th.text.strip() for th in table.find_all('th')]
        if "Player" in headers and "Runs" in headers:
            target_table = table
            break

    if not target_table:
        raise Exception("Stats table not found.")

    # Fix duplicate and empty headers
    raw_headers = [th.text.strip() for th in target_table.find_all('th')]
    headers = []
    used = {}
    for i, h in enumerate(raw_headers):
        if h == '':
            h = f"Unknown_{i}"
        if h in used:
            used[h] += 1
            h = f"{h}_{used[h]}"
        else:
            used[h] = 1
        headers.append(h)

    # Extract rows
    data = []
    for row in target_table.find_all('tr')[1:]:
        cols = row.find_all('td')
        if cols:
            data.append([col.text.strip() for col in cols])

    return headers, data

# ✅ Streamlit app
def main():
    st.title("Batting Innings Stats (2000–2025, Test Matches)")
    st.write("Data scraped live from ESPNcricinfo Statsguru")

    try:
        soup = fetch_data()
        headers, data = extract_table_data(soup)
        df = pd.DataFrame(data, columns=headers)
        st.dataframe(df)

    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
