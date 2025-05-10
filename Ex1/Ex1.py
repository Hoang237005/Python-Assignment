from bs4 import BeautifulSoup as BS
from selenium import webdriver as wd
from selenium.webdriver.chrome.options import Options as CO
from selenium.webdriver.chrome.service import Service as CS
import pandas as pd
import matplotlib.pyplot as plot
import numpy as np

def process_age(age_str):
    if age_str:
        return age_str.split('-')[0]
    return age_str

driver_path = r'C:\Windows\chromedriver.exe'
options = CO()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
chrome_service = CS(executable_path=driver_path)
browser = wd.Chrome(service=chrome_service, options=options)

pages = {
    'standard': 'https://fbref.com/en/comps/9/stats/Premier-League-Stats#all_stats_standard',
    'keepers': "https://fbref.com/en/comps/9/keepers/Premier-League-Stats#all_stats_keeper",
    'shots' : "https://fbref.com/en/comps/9/shooting/Premier-League-Stats#all_stats_shooting",
    'passes': "https://fbref.com/en/comps/9/passing/Premier-League-Stats#all_stats_passing",
    'creation': "https://fbref.com/en/comps/9/gca/Premier-League-Stats#all_stats_gca",
    'defense' : "https://fbref.com/en/comps/9/defense/Premier-League-Stats#all_stats_defense",
    'ball_control' : "https://fbref.com/en/comps/9/possession/Premier-League-Stats#all_stats_possession",
    'additional' : "https://fbref.com/en/comps/9/misc/Premier-League-Stats#all_stats_misc"
}

browser.get(pages['standard'])
html = browser.page_source
parser = BS(html, "html.parser")
main_table = parser.find('table', class_="min_width sortable stats_table shade_zero now_sortable sticky_table eq2 re2 le2")
headers = main_table.find_all('tr')[1]
headers = headers.find_all('th')
for idx in range(len(headers)):
    headers[idx] = headers[idx].text.strip()
headers = headers[1:]
headers[10], headers[11] ='Goals', 'Assists'
for idx in range(25, 35):
    headers[idx] = headers[idx] +'/90'
df = pd.DataFrame(columns=headers)
df = df.rename(columns={'MP': 'Matches', 'Min': 'Playing Time', 'CrdY': 'Yellows', 'CrdR': 'Reds'})
table_rows = main_table.find_all('tr')[2:]
idx = 0
for r in table_rows:
    cols = r.find_all('td')
    values = [col.text for col in cols]
    if len(values) == 36:
        df.loc[idx] = values
        idx += 1
df['Age'] = df['Age'].apply(process_age)
selected_cols = ['Player', 'Nation', 'Pos', 'Squad', 'Age', 'Matches', 'Starts', 'Playing Time', 'Goals', 'Assists', 'Yellows', 'Reds', 'xG', 'xAG', "PrgC", "PrgP","PrgR", 'Gls/90', 'Ast/90', 'xG/90', 'xAG/90']
df = df[selected_cols]

browser.get(pages['shots'])
html = browser.page_source
parser = BS(html, 'html.parser')
shooting_table = parser.find('table', class_="min_width sortable stats_table shade_zero now_sortable sticky_table eq2 re2 le2")
shoot_headers = shooting_table.find_all('tr')[1]
shoot_headers = shoot_headers.find_all('th')[1:]
for i in range(len(shoot_headers)):
    shoot_headers[i] = shoot_headers[i].text.strip()
shoot_df = pd.DataFrame(columns=shoot_headers)
shoot_rows = shooting_table.find_all('tr')[2:]
row_idx = 0
for r in shoot_rows:
    cells = r.find_all('td')
    vals = [cell.text for cell in cells]
    if len(vals) == len(shoot_headers):
        shoot_df.loc[row_idx] = vals
        row_idx += 1
keep_cols = ['Player', 'Squad', 'SoT%', 'SoT/90', 'G/Sh', 'Dist']
shoot_df = shoot_df[keep_cols]
df = pd.merge(df, shoot_df, on=['Player', 'Squad'], how='left')
df = df.drop_duplicates(keep='first')

browser.get(pages['passes'])
html = browser.page_source
parser = BS(html, 'html.parser')
pass_table = parser.find('table', class_="min_width sortable stats_table shade_zero now_sortable sticky_table eq2 re2 le2")
pass_headers = pass_table.find_all('tr')[1]
pass_headers = pass_headers.find_all('th')[1:]
for i in range(len(pass_headers)):
    pass_headers[i] = pass_headers[i].text.strip()
pass_headers[7], pass_headers[9], pass_headers[14], pass_headers[17], pass_headers[20] = 'Total_Cmp', 'Total_Cmp%' ,'Short_Cmp%', 'Medium_Cmp%','Long_Cmp%'
pass_df = pd.DataFrame(columns=pass_headers)
pass_rows = pass_table.find_all('tr')[2:]
row_idx = 0
for r in pass_rows:
    cells = r.find_all('td')
    vals = [cell.text for cell in cells]
    if len(vals) == len(pass_headers):
        pass_df.loc[row_idx] = vals
        row_idx += 1
keep_cols = ['Player','Squad', 'Total_Cmp', 'Total_Cmp%', 'TotDist', 'Short_Cmp%', 'Medium_Cmp%', 'Long_Cmp%', 'KP', '1/3', 'PPA', 'CrsPA', 'PrgP']
pass_df = pass_df[keep_cols].rename(columns={'PrgP':'(Passing)PrgP'})
df = pd.merge(df, pass_df, on=['Player', 'Squad'], how='left')
df = df.drop_duplicates(keep='first')

browser.get(pages['creation'])
html = browser.page_source
parser = BS(html, 'html.parser')
gca_table = parser.find('table', class_="min_width sortable stats_table shade_zero now_sortable sticky_table eq2 re2 le2")
gca_headers = gca_table.find_all('tr')[1]
gca_headers = gca_headers.find_all('th')[1:]
for i in range(len(gca_headers)):
    gca_headers[i] = gca_headers[i].text.strip()
gca_df = pd.DataFrame(columns=gca_headers)
gca_rows = gca_table.find_all('tr')[2:]
row_idx = 0
for r in gca_rows:
    cells = r.find_all('td')
    vals = [cell.text for cell in cells]
    if len(vals) == len(gca_headers):
        gca_df.loc[row_idx] = vals
        row_idx += 1
keep_cols = ['Player','Squad','SCA', 'SCA90', 'GCA', 'GCA90']
gca_df = gca_df[keep_cols]
df = pd.merge(df, gca_df, on=['Player','Squad'], how='left')
df = df.drop_duplicates(keep='first')

browser.get(pages['defense'])
html = browser.page_source
parser = BS(html, 'html.parser')
def_table = parser.find('table', id="stats_defense")
def_headers = def_table.find_all('tr')[1]
def_headers = def_headers.find_all('th')
for i in range(len(def_headers)):
    def_headers[i] = def_headers[i].text.strip()
def_headers[13] = 'challenges' + def_headers[13]
def_headers = def_headers[1:]
def_df = pd.DataFrame(columns=def_headers)
def_rows = def_table.find_all('tr')[2:]
row_idx = 0
for r in def_rows:
    cells = r.find_all('td')
    vals = [cell.text for cell in cells]
    if len(vals) == len(def_headers):
        def_df.loc[row_idx] = vals
        row_idx += 1
keep_cols = ['Player', 'Squad', 'Tkl', 'TklW', 'Att', 'Lost', 'Blocks', 'Sh', 'Pass', 'Int']
def_df = def_df[keep_cols]
df = pd.merge(df, def_df, on=['Player', 'Squad'], how='left')
df = df.drop_duplicates(keep='first')

browser.get(pages['ball_control'])
html = browser.page_source
parser = BS(html, 'html.parser')
pos_table = parser.find('table', class_="min_width sortable stats_table shade_zero now_sortable sticky_table eq2 re2 le2")
pos_headers = pos_table.find_all('tr')[1]
pos_headers = pos_headers.find_all('th')
pos_headers = pos_headers[1:]
for i in range(len(pos_headers)):
    pos_headers[i] = pos_headers[i].text.strip()
pos_headers[14], pos_headers[22], pos_headers[23], pos_headers[28] = 'Take-Ons_' + pos_headers[14], 'Carries_' + pos_headers[22], 'Carries_' + pos_headers[23], 'Receiving_' + pos_headers[28]
pos_df = pd.DataFrame(columns=pos_headers)
pos_rows = pos_table.find_all('tr')[2:]
row_idx = 0
for r in pos_rows:
    cells = r.find_all('td')
    vals = [cell.text for cell in cells]
    if len(vals) == len(pos_headers):
        pos_df.loc[row_idx] = vals
        row_idx += 1
keep_cols = ['Player', 'Squad', 'Touches', 'Def Pen', 'Def 3rd', 'Mid 3rd', 'Att 3rd', 'Att Pen', 'Take-Ons_Att', 'Succ%', 'Tkld%', 'Carries', 'PrgDist', 'Carries_PrgC', 'Carries_1/3', 'CPA', 'Mis', 'Dis', 'Rec', 'Receiving_PrgR']
pos_df = pos_df[keep_cols]
df = pd.merge(df, pos_df, on=['Player', 'Squad'], how='left')

browser.get(pages['additional'])
html = browser.page_source
parser = BS(html, 'html.parser')
misc_table = parser.find('table', class_="min_width sortable stats_table shade_zero now_sortable sticky_table eq2 re2 le2")
misc_headers = misc_table.find_all('tr')[1]
misc_headers = misc_headers.find_all('th')
misc_headers = misc_headers[1:]
for i in range(len(misc_headers)):
    misc_headers[i] = misc_headers[i].text.strip()
misc_df = pd.DataFrame(columns=misc_headers)
misc_rows = misc_table.find_all('tr')[2:]
row_idx = 0
for r in misc_rows:
    cells = r.find_all('td')
    vals = [cell.text for cell in cells]
    if len(vals) == len(misc_headers):
        misc_df.loc[row_idx] = vals
        row_idx += 1
keep_cols = ['Player', 'Squad', 'Fls', 'Fld', 'Off', 'Crs', 'Recov', 'Won', 'Lost', 'Won%']
misc_df = misc_df[keep_cols].rename(columns={'Lost': '(Misc)Lost'})
df = pd.merge(df, misc_df, on=['Player', 'Squad'], how='left')

browser.get(pages['keepers'])
html = browser.page_source
parser = BS(html, 'html.parser')
gk_table = parser.find('table', id="stats_keeper")
gk_headers = gk_table.find_all('tr')[1]
gk_headers = gk_headers.find_all('th')[1:]
for i in range(len(gk_headers)):
    gk_headers[i] = gk_headers[i].text.strip()
gk_headers[24] = "Penalty_" + gk_headers[24]
gk_df = pd.DataFrame(columns=gk_headers)
gk_rows = gk_table.find_all('tr')[2:]
row_idx = 0
for r in gk_rows:
    cells = r.find_all('td')
    vals = [cell.text for cell in cells]
    if len(vals) == len(gk_headers):
        gk_df.loc[row_idx] = vals
        row_idx += 1

keep_cols = ['Player', 'Squad', 'GA90', 'Save%', 'CS%', 'Penalty_Save%']
gk_df = gk_df[keep_cols]
df = pd.merge(df, gk_df, on=['Player', 'Squad'], how='left')

df['Playing Time'] = pd.to_numeric(
    df['Playing Time'].astype(str).str.replace(',', '', regex=False),
    errors='coerce'
)
df = df[df['Playing Time'] > 90].sort_values(by='Player').reset_index(drop=True)
df = df.replace('', np.nan)
df = df.fillna('N/a')
df = df.rename(columns={'Pos':'Position', 'Squad':'Team'})
df.to_csv('Exercise 1/result.csv', na_rep='N/a', index=False)

print("Data successfully saved to result.csv")
browser.quit()