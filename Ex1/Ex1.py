import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium import webdriver
from bs4 import BeautifulSoup

# Data processing functions
def extract_age(age_str):
    return age_str.split('-')[0] if age_str else age_str

# Configuration and setup
chrome_config = {
    'executable_path': r'C:\Windows\chromedriver.exe',
    'options': ['--headless', '--disable-gpu']
}

# Initialize web driver
service = ChromeService(executable_path=chrome_config['executable_path'])
options = ChromeOptions()
for arg in chrome_config['options']:
    options.add_argument(arg)
driver = webdriver.Chrome(service=service, options=options)

# Data collection URLs
data_sources = {
    'players': 'https://fbref.com/en/comps/9/stats/Premier-League-Stats#all_stats_standard',
    'keepers': "https://fbref.com/en/comps/9/keepers/Premier-League-Stats#all_stats_keeper",
    'shooting': "https://fbref.com/en/comps/9/shooting/Premier-League-Stats#all_stats_shooting",
    'passing': "https://fbref.com/en/comps/9/passing/Premier-League-Stats#all_stats_passing",
    'creation': "https://fbref.com/en/comps/9/gca/Premier-League-Stats#all_stats_gca",
    'defense': "https://fbref.com/en/comps/9/defense/Premier-League-Stats#all_stats_defense",
    'possession': "https://fbref.com/en/comps/9/possession/Premier-League-Stats#all_stats_possession",
    'misc_stats': "https://fbref.com/en/comps/9/misc/Premier-League-Stats#all_stats_misc"
}

# Helper function for table processing
def process_table_data(url, table_class=None, table_id=None, rename_cols=None):
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    table = soup.find('table', class_=table_class, id=table_id)
    
    headers = [th.text.strip() for th in table.find_all('tr')[1].find_all('th')]
    if rename_cols:
        for old, new in rename_cols.items():
            if old in headers:
                headers[headers.index(old)] = new
    
    data = []
    for row in table.find_all('tr')[2:]:
        row_data = [td.text for td in row.find_all('td')]
        if len(row_data) == len(headers[1:]):  # Skip header row th
            data.append(row_data)
    
    return pd.DataFrame(data, columns=headers[1:])

# Main data processing
def collect_player_stats():
    # Standard stats
    standard_rename = {
        'MP': 'Match Played', 
        'Min': 'Minutes', 
        'CrdY': 'Yellow Cards', 
        'CrdR': 'Red Cards'
    }
    df = process_table_data(
        data_sources['players'],
        table_class="min_width sortable stats_table shade_zero now_sortable sticky_table eq2 re2 le2",
        rename_cols=standard_rename
    )
    
    # Process age and columns
    df['Age'] = df['Age'].apply(extract_age)
    per_90_cols = [f'{col}/90' for col in ['Gls', 'Ast', 'xG', 'xAG']]
    standard_cols = [
        'Player', 'Nation', 'Pos', 'Squad', 'Age', 'Match Played', 
        'Starts', 'Minutes', 'Goals', 'Assists', 'Yellow Cards', 
        'Red Cards', 'xG', 'xAG', "PrgC", "PrgP", "PrgR"
    ]
    df = df[standard_cols + per_90_cols]

    # Shooting stats
    shooting_df = process_table_data(
        data_sources['shooting'],
        table_class="min_width sortable stats_table shade_zero now_sortable sticky_table eq2 re2 le2"
    )
    shooting_cols = ['Player', 'Squad', 'SoT%', 'SoT/90', 'G/Sh', 'Dist']
    df = pd.merge(df, shooting_df[shooting_cols], on=['Player', 'Squad'], how='left')

    # Passing stats
    passing_rename = {
        'PrgP': '(Passing)PrgP',
        '7': 'Total_Cmp',
        '9': 'Total_Cmp%',
        '14': 'Short_Cmp%',
        '17': 'Medium_Cmp%',
        '20': 'Long_Cmp%'
    }
    passing_df = process_table_data(
        data_sources['passing'],
        table_class="min_width sortable stats_table shade_zero now_sortable sticky_table eq2 re2 le2",
        rename_cols=passing_rename
    )
    passing_cols = [
        'Player', 'Squad', 'Total_Cmp', 'Total_Cmp%', 'TotDist', 
        'Short_Cmp%', 'Medium_Cmp%', 'Long_Cmp%', 'KP', '1/3', 
        'PPA', 'CrsPA', '(Passing)PrgP'
    ]
    df = pd.merge(df, passing_df[passing_cols], on=['Player', 'Squad'], how='left')

    # Goal and shot creation
    creation_df = process_table_data(
        data_sources['creation'],
        table_class="min_width sortable stats_table shade_zero now_sortable sticky_table eq2 re2 le2"
    )
    creation_cols = ['Player', 'Squad', 'SCA', 'SCA90', 'GCA', 'GCA90']
    df = pd.merge(df, creation_df[creation_cols], on=['Player', 'Squad'], how='left')

    # Defensive actions
    defense_df = process_table_data(
        data_sources['defense'],
        table_id="stats_defense"
    )
    defense_df.columns = [f'challenges{col}' if i == 13 else col for i, col in enumerate(defense_df.columns)]
    defense_cols = ['Player', 'Squad', 'Tkl', 'TklW', 'Att', 'Lost', 'Blocks', 'Sh', 'Pass', 'Int']
    df = pd.merge(df, defense_df[defense_cols], on=['Player', 'Squad'], how='left')

    # Possession stats
    possession_df = process_table_data(
        data_sources['possession'],
        table_class="min_width sortable stats_table shade_zero now_sortable sticky_table eq2 re2 le2"
    )
    possession_df.columns = [
        f'Take-Ons_{col}' if i == 14 else
        f'Carries_{col}' if i in [22, 23] else
        f'Receiving_{col}' if i == 28 else
        col for i, col in enumerate(possession_df.columns)
    ]
    possession_cols = [
        'Player', 'Squad', 'Touches', 'Def Pen', 'Def 3rd', 'Mid 3rd', 
        'Att 3rd', 'Att Pen', 'Take-Ons_Att', 'Succ%', 'Tkld%', 
        'Carries', 'PrgDist', 'Carries_PrgC', 'Carries_1/3', 
        'CPA', 'Mis', 'Dis', 'Rec', 'Receiving_PrgR'
    ]
    df = pd.merge(df, possession_df[possession_cols], on=['Player', 'Squad'], how='left')

    # Miscellaneous stats
    misc_df = process_table_data(
        data_sources['misc_stats'],
        table_class="min_width sortable stats_table shade_zero now_sortable sticky_table eq2 re2 le2"
    )
    misc_cols = ['Player', 'Squad', 'Fls', 'Fld', 'Off', 'Crs', 'Recov', 'Won', 'Lost', 'Won%']
    df = pd.merge(df, misc_df[misc_cols].rename(columns={'Lost': '(Misc)Lost'}), on=['Player', 'Squad'], how='left')

    # Goalkeeping stats
    goalkeeping_df = process_table_data(
        data_sources['keepers'],
        table_id="stats_keeper"
    )
    goalkeeping_df.columns = [f'Penalty_{col}' if i == 24 else col for i, col in enumerate(goalkeeping_df.columns)]
    goalkeeping_cols = ['Player', 'Squad', 'GA90', 'Save%', 'CS%', 'Penalty_Save%']
    df = pd.merge(df, goalkeeping_df[goalkeeping_cols], on=['Player', 'Squad'], how='left')

    # Final processing
    df['Minutes'] = pd.to_numeric(df['Minutes'].str.replace(',', ''), errors='coerce')
    df = df[df['Minutes'] > 90].sort_values('Player').reset_index(drop=True)
    df = df.replace('', np.nan).fillna('N/a')
    df = df.rename(columns={'Pos': 'Position', 'Squad': 'Team'})
    
    return df

# Execute and save results
if __name__ == "__main__":
    final_data = collect_player_stats()
    final_data.to_csv('Exercise 1/result.csv', na_rep='N/a', index=False)
    print("Statistical data successfully exported to result.csv")
    driver.quit()
