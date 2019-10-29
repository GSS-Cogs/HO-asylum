# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.2.4
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# Table as_19_q: Refugees (and others) resettled, including dependants, by country of nationality 

# +
from gssutils import *

scraper = Scraper('https://www.gov.uk/government/statistics/immigration-statistics-october-to-december-2017-data-tables')
scraper
# -

dist = scraper.distribution(
    title='Asylum data tables immigration statistics October to December 2017 volume 4')
sheets = dist.as_pandas()
sheets.keys()

# Metadata is in the spreadsheet 'Contents' tab.

# +
TAB_NAME = 'as_19_q'

contents = sheets['Contents'].iloc[7:].copy()
contents.rename(columns=contents.iloc[0], inplace=True)
contents.drop(contents.index[0], inplace=True)
metadata = contents[contents['Table'] == TAB_NAME].iloc[0]
display(metadata)
scraper.dataset.comment = f'{scraper.dataset.title}: table "{TAB_NAME}"'
scraper.dataset.title = metadata['Title']
scraper.dataset.issued = metadata['Last updated']
scraper.dataset.updateDueOn = metadata['Next planned update']
del scraper.dataset.description
scraper.dataset
# -

observations = sheets[TAB_NAME].loc[3:, :5]
observations.rename(columns= observations.iloc[0], inplace=True)
observations.drop(observations.index[0], inplace = True)
Final_table = pd.melt(observations,
                       ['Year','Country of nationality'],
                       var_name= 'Resettlement Scheme',
                       value_name="Value")
Final_table.Value.dropna(inplace =True)
Final_table.rename(columns={'Country of nationality': 'Nationality'}, inplace=True)
Final_table['Unit'] = 'refugees-and-dependants'
Final_table['Measure Type'] = 'Count'

Final_table['Value'] = Final_table['Value'].map(lambda x : ''
                                                   if (x == '.') | (x == 'z') | ( x == ':')
                                                    else x )

import numpy as np
Final_table['Value'].replace('', np.nan, inplace=True)
Final_table.dropna(subset=['Value'], inplace=True)
Final_table['Value'] = Final_table['Value'].apply(lambda x: pd.to_numeric(x, downcast='integer'))
Final_table['Value'] = Final_table['Value'].astype(int)

Final_table.rename(columns={'Year': 'Period'}, inplace=True)
Final_table['Period'] = Final_table['Period'].astype(str)
Final_table = Final_table[Final_table['Period'] != '']

# +
import re
YEAR_RE = re.compile(r'[0-9]{4}')
YEAR_MONTH_RE = re.compile(r'([0-9]{4})\s+(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)')
YEAR_QUARTER_RE = re.compile(r'([0-9]{4})\s+(Q[1-4])')

class Re(object):
  def __init__(self):
    self.last_match = None
  def fullmatch(self,pattern,text):
    self.last_match = re.fullmatch(pattern,text)
    return self.last_match

def time2period(t):
    gre = Re()
    if gre.fullmatch(YEAR_RE, t):
        return f"year/{t}"
    elif gre.fullmatch(YEAR_MONTH_RE, t):
        year, month = gre.last_match.groups()
        month_num = {'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04', 'MAY': '05', 'JUN': '06',
                     'JUL': '07', 'AUG': '08', 'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'}.get(month)
        return f"month/{year}-{month_num}"
    elif gre.fullmatch(YEAR_QUARTER_RE, t):
        year, quarter = gre.last_match.groups()
        return f"quarter/{year}-{quarter}"
    else:
        print(f"no match for {t}")

Final_table['Period'] = Final_table['Period'].apply(time2period)
# -

Final_table['Nationality'] = Final_table['Nationality'].str.lstrip('*')

Final_table['Nationality'] = Final_table['Nationality'].map(
    lambda x: {
        'Afghanistan ' : 'Afghanistan',
        'Total': 'Rest of world'
        }.get(x, x))

Final_table['Resettlement Scheme'] = Final_table['Resettlement Scheme'].map(
    lambda x: {
        'Gateway Protection Programme' : 'gateway',
        'Mandate Scheme' : 'mandate',
        'Vulnerable Persons Resettlement Scheme' : 'vulnerable-persons',
        'Vulnerable Children Resettlement Scheme' : 'vulnerable-children'
        }.get(x, x))

import urllib.request as request
import csv
import io
import requests
r = request.urlopen('https://raw.githubusercontent.com/ONS-OpenData/ref_migration/master/codelists/ho-country-of-nationality.csv').read().decode('utf8').split("\n")
reader = csv.reader(r)
url="https://raw.githubusercontent.com/ONS-OpenData/ref_migration/master/codelists/ho-country-of-nationality.csv"
s=requests.get(url).content
c=pd.read_csv(io.StringIO(s.decode('utf-8')))
Final_table = pd.merge(Final_table, c, how = 'left', left_on = 'Nationality', right_on = 'Label')
Final_table.columns = ['HO Country of Nationality' if x=='Notation' else x for x in Final_table.columns]


# +
def user_perc(x,y):
    
    if str(x) == 'Vulnerable Children Resettlement Scheme' :
        return 'Refugees and dependents'
    else:
        return y
    
Final_table['Unit'] = Final_table.apply(lambda row: user_perc(row['Resettlement Scheme'],row['Unit']), axis = 1)

# -

Final_table = Final_table[['Period','HO Country of Nationality','Resettlement Scheme','Measure Type','Value','Unit']]

# +
destinationFolder = Path('out')
destinationFolder.mkdir(exist_ok=True, parents=True)

Final_table.drop_duplicates().to_csv(destinationFolder / f'{TAB_NAME}.csv', index = False)

# +
from gssutils.metadata import THEME

scraper.dataset.family = 'migration'
scraper.dataset.theme = THEME['population']
scraper.set_base_uri('http://gss-data.org.uk')
scraper.set_dataset_id(f'migration/ho-asylum/{TAB_NAME}')
with open(destinationFolder / f'{TAB_NAME}.csv-metadata.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())
# -

schema = CSVWMetadata('https://gss-cogs.github.io/ref_migration/')
schema.create(destinationFolder / f'{TAB_NAME}.csv', destinationFolder / f'{TAB_NAME}.csv-schema.json')

Final_table


