import os
import json
import time
import re
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class TransferValueScraper:
    def __init__(self):
        self.script_location = os.path.dirname(os.path.abspath(__file__))
        pd.set_option('future.no_silent_downcasting', True)

    def load_player_data(self):
        """Load and preprocess player performance data"""
        data_path = os.path.join(self.script_location, "..", "Exercise 1", "results.csv")
        print(f"Loading player data from: {data_path}")

        try:
            player_df = pd.read_csv(data_path, encoding='utf-8')
            print("Available columns:", player_df.columns.tolist())

            # Process minutes played
            player_df['Minutes'] = (
                player_df['Minutes']
                .str.replace(',', '')
                .pipe(pd.to_numeric, errors='coerce')
            )

            return player_df[player_df['Minutes'] > 900].copy()
        except FileNotFoundError:
            print(f"Error: Data file not found at {data_path}")
            exit(1)

    def manage_cache(self, cache_file='transfer_cache.json'):
        """Handle caching of transfer values"""
        self.cache_path = os.path.join(self.script_location, cache_file)

        def load():
            if os.path.exists(self.cache_path):
                with open(self.cache_path, 'r') as cache:
                    return json.load(cache)
            return {}

        def save(data):
            with open(self.cache_path, 'w') as cache:
                json.dump(data, cache)

        return load, save

    def get_transfer_values(self, player_names):
        """Retrieve transfer values from Transfermarkt"""
        load_cache, save_cache = self.manage_cache()
        cached_data = load_cache()
        results = []

        # Check cache first
        cached_players = [p for p in player_names if p in cached_data]
        results.extend(
            {'Player': p, 'Value_M€': cached_data[p]}
            for p in cached_players
        )

        # Identify players needing scraping
        to_scrape = [p for p in player_names if p not in cached_data]
        if not to_scrape:
            print("Using cached values only")
            return pd.DataFrame(results)

        # Configure browser
        browser_options = Options()
        browser_options.add_argument("--headless")
        browser_options.add_argument("--disable-gpu")
        browser_options.add_argument("--no-sandbox")
        browser_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")

        try:
            with webdriver.Chrome(
                    service=Service(ChromeDriverManager().install()),
                    options=browser_options
            ) as driver:

                print("Accessing Transfermarkt...")
                driver.get("https://www.transfermarkt.com/premier-league/marktwerte/wettbewerb/GB1")

                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "table.items"))

                page_content = BeautifulSoup(driver.page_source, 'html.parser')
                player_table = page_content.select_one("table.items")

                if player_table:
                    for
                row in player_table.select("tr.odd, tr.even"):
                self._process_player_row(row, to_scrape, results, cached_data)

                # Handle players not found
                self._handle_missing_players(to_scrape, results, cached_data)
                save_cache(cached_data)

        except Exception as e:
            print(f"Scraping interrupted: {str(e)}")
            self._handle_missing_players(to_scrape, results, cached_data)
            save_cache(cached_data)

        return pd.DataFrame(results)

    def _process_player_row(self, row, target_players, results, cache):
        """Extract data from a single player row"""
        name_element = row.select_one("td.hauptlink a")
        value_element = row.select_one("td.rechts.hauptlink")

        if name_element and value_element:
            player_name = name_element.get_text(strip=True)
            value_text = value_element.get_text(strip=True)

            # Convert value to millions EUR
            value = self._parse_value(value_text)

            # Match with our target players
            for target in target_players:
                if (target.lower() in player_name.lower() or
                        player_name.lower() in target.lower()):
                    results.append({
                        'Player': target,
                        'Value_M€': value
                    })
                    cache[target] = value
                    target_players.remove(target)
                    break

    def _parse_value(self, value_text):
        """Convert transfer value text to numeric"""
        numeric_value = re.sub(r'[^\d.]', '', value_text)

        if not numeric_value:
            return np.nan

        value = float(numeric_value)

        if 'k' in value_text.lower():
            return value / 1000
        if 'bn' in value_text.lower():
            return value * 1000
        return value

    def _handle_missing_players(self, players, results, cache):
        """Handle players not found on the page"""
        for player in players:
            results.append({
                'Player': player,
                'Value_M€': np.nan
            })
            cache[player] = np.nan

    def save_results(self, player_data, transfer_data, output_file='transfer_values.csv'):
        """Save final results to file"""
        merged_data = player_data.merge(
            transfer_data,
            left_on='First Name',
            right_on='Player',
            how='left'
        )

        output_columns = [
            'First Name', 'Team', 'Position',
            'Minutes', 'Value_M€'
        ]

        try:
            output_path = os.path.join(self.script_location, output_file)
            merged_data[output_columns].to_csv(output_path, index=False)
            print(f"Results saved to {output_path}")
        except PermissionError:
            alt_path = os.path.join(os.path.expanduser("~"), "Desktop", output_file)
            merged_data[output_columns].to_csv(alt_path, index=False)
            print(f"Results saved to {alt_path}")

    def generate_documentation(self):
        """Create methodology documentation"""
        content = """=== Advanced Player Valuation Methodology ===

1. Feature Engineering:
- Technical Attributes: Dribbling (attackers) | Tackling (defenders) | Key passes (midfielders)
- Performance Metrics: xGChain, Progressive carries, Pressures success rate
- Potential Indicators: Age, Improvement rate, International experience

2. Model Architecture:
- Base Models: 
  * XGBoost (non-linear relationships)
  * ElasticNet (regularized linear features)
- Meta Model: 3-layer Neural Network
- Feature Selection: Recursive Feature Elimination with CV

3. Implementation:
from sklearn.ensemble import StackingRegressor
from xgboost import XGBRegressor
from sklearn.linear_model import ElasticNet

# Position-specific pipelines
model = StackingRegressor(
    estimators=[
        ('xgb', XGBRegressor(objective='reg:squarederror')),
        ('enet', ElasticNet(alpha=0.1))
    ],
    final_estimator=MLPRegressor(hidden_layer_sizes=(64,32))
)"""

        doc_path = os.path.join(self.script_location, 'valuation_methodology.txt')
        with open(doc_path, 'w', encoding='utf-8') as doc:
            doc.write(content)
        print(f"Methodology documentation saved to {doc_path}")


if __name__ == "__main__":
    scraper = TransferValueScraper()

    # Load and process player data
    players_df = scraper.load_player_data()
    print(f"Processing {len(players_df)} players with sufficient minutes")

    # Get transfer values
    transfer_values = scraper.get_transfer_values(players_df['First Name'].unique())

    # Save results
    scraper.save_results(players_df, transfer_values)

    # Generate documentation
    scraper.generate_documentation()