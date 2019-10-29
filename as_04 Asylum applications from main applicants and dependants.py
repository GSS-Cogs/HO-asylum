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

# as_04: Asylum applications from main applicants and dependants, by age, sex and country of nationality

# +
from gssutils import *

scraper = Scraper('https://www.gov.uk/government/statistics/immigration-statistics-october-to-december-2017-data-tables')
scraper
# -

dist = scraper.distribution(
    title='Asylum data tables immigration statistics October to December 2017 volume 2 second edition')
sheets = dist.as_pandas()
sheets.keys()

# Metadata is in the spreadsheet 'Contents' tab

# +
TAB_NAME = 'as_04'

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

# https://www.gov.uk/government/uploads/system/uploads/attachment_data/file/691964/asylum2-oct-dec-2017-tables.ods

observations = sheets[TAB_NAME].loc[3:, :36]
observations.rename(columns= observations.iloc[0], inplace=True)
observations.drop(observations.index[0], inplace = True)
observations.drop('Geographical region', axis = 1, inplace = True)
Final_table = pd.melt(observations,
                       ['Year','Country of nationality'],
                       var_name= 'Application',
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

Final_table.rename(columns={'Year': 'Period'}, inplace=True)
Final_table['Period'] = Final_table['Period'].astype(str)
Final_table = Final_table[Final_table['Period'] != '']
Final_table['Period'] = 'year/' + Final_table['Period'].map(lambda cell: cell.replace(' ','-'))

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

Final_table = Final_table[['HO Country of Nationality','Period','Application','Measure Type','Value','Unit']]

Final_table['Age'] = Final_table['Application'].map(
    lambda x: {
        'Total Applications' : 'all',
        'Total male applications' : 'all', 
        'Male: \nunder 5' : 'hoad/under-5',
         'Male: 5-9' : 'hoad/5-9', 
        'Male: 10-13' : 'hoad/10-13', 
        'Male: 14-15' : 'hoad/14-15', 
        'Male: 16-17' : 'hoad/16-17',
         'Male: 18-20' : 'hoad/18-20', 
        'Male: 21-24' : 'hoad/21-24', 
        'Male: 25-29' : 'hoad/25-29', 
        'Male: 30-34' : 'hoad/30-34',
         'Male: 35-39' : 'hoad/35-39', 
        'Male: 40-49' : 'hoad/40-49', 
        'Male: 50-59': 'hoad/50-59', 
        'Male: 60-64' : 'hoad/60-64',
        'Male: 65+' : 'hoad/65-plus', 
        'Male: Age unknown' : 'hoad/unknown', 
        'Total female applications' : 'all',
        'Female: under 5' : 'hoad/under-5', 
        'Female: \n5-9' : 'hoad/5-9', 
        'Female: 10-13' : 'hoad/10-13',
         'Female: 14-15' : 'hoad/14-15', 
        'Female: 16-17' : 'hoad/16-17', 
        'Female: 18-20' : 'hoad/18-20', 
        'Female: 21-24': 'hoad/21-24',
        'Female: 25-29' : 'hoad/25-29', 
        'Female: 30-34': 'hoad/30-34', 
        'Female: 35-39' : 'hoad/35-39', 
        'Female: 40-49' : 'hoad/40-49',
         'Female: 50-59' : 'hoad/50-59', 
        'Female: 60-64' : 'hoad/60-64', 
        'Female: \n65+': 'hoad/65-plus',
        'Female: Age unknown' : 'hoad/unknown', 
        'Sex unknown' : 'hoad/unknown'
        }.get(x, x))

Final_table['Sex'] = Final_table['Application'].map(
    lambda x: {
        'Total Applications' : 'T',
        'Total male applications' : 'M', 
        'Male: \nunder 5' : 'M',
         'Male: 5-9' : 'M', 
        'Male: 10-13' : 'M', 
        'Male: 14-15' : 'M', 
        'Male: 16-17' : 'M',
         'Male: 18-20' : 'M', 
        'Male: 21-24' : 'M', 
        'Male: 25-29' : 'M', 
        'Male: 30-34' : 'M',
         'Male: 35-39' : 'M', 
        'Male: 40-49' : 'M', 
        'Male: 50-59': 'M', 
        'Male: 60-64' : 'M',
        'Male: 65+' : 'M', 
        'Male: Age unknown' : 'M', 
        'Total female applications' : 'F',
        'Female: under 5' : 'F', 
        'Female: \n5-9' : 'F', 
        'Female: 10-13' : 'F',
         'Female: 14-15' : 'F', 
        'Female: 16-17' : 'F', 
        'Female: 18-20' : 'F', 
        'Female: 21-24': 'F',
        'Female: 25-29' : 'F', 
        'Female: 30-34': 'F', 
        'Female: 35-39' : 'F', 
        'Female: 40-49' : 'F',
         'Female: 50-59' : 'F', 
        'Female: 60-64' : 'F', 
        'Female: \n65+': 'F',
        'Female: Age unknown' : 'F', 
        'Sex unknown' : 'U'
        }.get(x, x))

Final_table = Final_table[['HO Country of Nationality','Period','Age','Sex','Measure Type','Value','Unit']]

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
