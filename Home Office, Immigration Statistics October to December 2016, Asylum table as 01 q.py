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

# Home Office, Immigration Statistics October to December 2016, Asylum table as 01 q (Asylum volume 1)

# +
from gssutils import *

scraper = Scraper('https://www.gov.uk/government/statistics/immigration-statistics-october-to-december-2017-data-tables')
scraper
# -

dist = scraper.distribution(
    title='Asylum data tables immigration statistics October to December 2017 volume 1 second edition'
)
sheets = dist.as_pandas()
sheets.keys()

# Metadata is in the spreadsheet 'Contents' tab

# +
TAB_NAME = 'as_01_q'

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

observations = sheets[TAB_NAME].loc[3:, :26]
observations.rename(columns= observations.iloc[0], inplace=True)
observations.drop(observations.index[0], inplace = True)
observations.drop('Geographical region', axis = 1, inplace = True)
Final_table = pd.melt(observations,
                       ['Quarter','Country of nationality'],
                       var_name= 'Asylum Application',
                       value_name="Value")
Final_table.Value.dropna(inplace =True)
Final_table.rename(columns={'Country of nationality': 'Nationality'}, inplace=True)
Final_table['Unit'] = 'applications'
Final_table['Measure Type'] = 'Count'

Final_table['Value'] = Final_table['Value'].map(lambda x : ''
                                                   if (x == '.') | (x == 'z') | ( x == ':')
                                                    else x )

import numpy as np
Final_table['Value'].replace('', np.nan, inplace=True)
Final_table.dropna(subset=['Value'], inplace=True)
Final_table['Value'] = Final_table['Value'].apply(lambda x: pd.to_numeric(x, downcast='integer'))
Final_table['Value'] = Final_table['Value'].astype(int)

Final_table.rename(columns={'Quarter': 'Period'}, inplace=True)
Final_table['Period'] = Final_table['Period'].astype(str)
Final_table = Final_table[Final_table['Period'] != '']
Final_table['Period'] = 'quarter/' + Final_table['Period'].map(lambda cell: cell.replace(' ','-'))

Final_table['Nationality'] = Final_table['Nationality'].str.lstrip('*')

Final_table['Nationality'] = Final_table['Nationality'].map(
    lambda x: {
        'Total Africa North' : 'Africa North',
        'Total Africa Sub-Saharan' : 'Africa Sub-Saharan',
        'Total America North' : 'America North',
        'Total America Central and South ' : 'America Central and South',
        'Total Asia Central' : 'Asia Central',
        'Total Asia East' : 'Asia East',
        'Total Asia South' : 'Asia South',
        'Total Asia South East' : 'Asia South East',
        'Total EU 14' : 'EU 14',
        'Total EU 2' : 'EU 2',
        'Total EU 8' : 'EU 8',
        'Total EU Other' : 'EU Other',
        'Total Europe Other' : 'Europe Other',
        'Total Middle East' : 'Middle East',
        'Total Oceania' : 'Oceania',
        'Total Other' : 'Other',
        'Total': 'Rest of world'
        }.get(x, x))

# +
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
# -

Final_table = Final_table[['HO Country of Nationality','Period','Asylum Application','Measure Type','Value','Unit']]

Final_table['Asylum Application'] = Final_table['Asylum Application'].map(
    lambda x: {
        'Pending further \nreview': 'Pending further review',
        'Other \ngrants' : 'Other grants',
        'Total pending initial \ndecision' : 'Total pending initial decision'                
        }.get(x, x))

for col in Final_table.columns:
    if col not in ['Value', 'Period']:
        Final_table[col] = Final_table[col].astype('category')
        display(col)
        display(Final_table[col].cat.categories)

# +
import urllib.request as request
import csv
import io
import requests
r = request.urlopen('https://raw.githubusercontent.com/ONS-OpenData/ref_migration/master/codelists/asylum-application-status.csv').read().decode('utf8').split("\n")
reader = csv.reader(r)

url="https://raw.githubusercontent.com/ONS-OpenData/ref_migration/master/codelists/asylum-application-status.csv"
s=requests.get(url).content
c=pd.read_csv(io.StringIO(s.decode('utf-8')))
Final_table = pd.merge(Final_table, c, how = 'left', left_on = 'Asylum Application', right_on = 'Label')
Final_table.columns = ['Asylum Application Status' if x=='Notation' else x for x in Final_table.columns]
# -

Final_table = Final_table[['HO Country of Nationality','Period','Asylum Application Status','Measure Type','Value','Unit']]

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
