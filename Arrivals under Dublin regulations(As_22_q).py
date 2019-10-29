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

# Table as_ 22_q: Arrivals, and requests for transfer into the UK under the Dublin Regulation, by article and country of transfer

# +
from gssutils import *

scraper = Scraper('https://www.gov.uk/government/statistics/immigration-statistics-october-to-december-2017-data-tables')
scraper
# -

dist = scraper.distribution(
    title='Asylum data tables immigration statistics October to December 2017 volume 5')
sheets = dist.as_pandas()
sheets.keys()

# Metadata is in the spreadsheet 'Contents' tab

# +
TAB_NAME = 'as_22_q'

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

Final_table = pd.DataFrame()

observations = sheets[TAB_NAME].loc[3:, :15]
observations.rename(columns= observations.iloc[0], inplace=True)
observations.drop(observations.index[0], inplace = True)
new_table = pd.melt(observations,
                       ['Quarter','Country Transferred from '],
                       var_name="Total arrivals into the UK",
                       value_name="Value")
new_table.Value.dropna(inplace =True)
new_table.rename(columns={'Total arrivals into the UK': 'Dublin Regulation Article'}, inplace=True)
new_table['Nature of Transfer'] = 'arrivals'
new_table['Unit'] = 'arrivals'
new_table['Measure Type'] = 'Count'
Final_table = pd.concat([Final_table, new_table])

observations1 = sheets[TAB_NAME].loc[3:, :30]
observations1.drop(observations1.iloc[: , 2:16], inplace=True, axis=1)
observations1.rename(columns= observations1.iloc[0], inplace=True)
observations1.drop(observations1.index[0], inplace = True)
new_table = pd.melt(observations1,
                       ['Quarter','Country Transferred from '],
                       var_name="Total requests for transfers into the UK",
                       value_name="Value")
new_table.Value.dropna(inplace =True)
new_table.rename(columns={'Total requests for transfers into the UK': 'Dublin Regulation Article'}, inplace=True)
new_table['Nature of Transfer'] = 'requests-for-transfer'
new_table['Unit'] = 'requests-for-transfer'
new_table['Measure Type'] = 'Count'
Final_table = pd.concat([Final_table, new_table])

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

Final_table['Country Transferred'] = Final_table['Country Transferred from '].str.lstrip('*')

import urllib.request as request
import csv
import io
import requests
r = request.urlopen('https://raw.githubusercontent.com/ONS-OpenData/ref_migration/master/codelists/foreign-geography.csv').read().decode('utf8').split("\n")
reader = csv.reader(r)
url="https://raw.githubusercontent.com/ONS-OpenData/ref_migration/master/codelists/foreign-geography.csv"
s=requests.get(url).content
c=pd.read_csv(io.StringIO(s.decode('utf-8')))
Final_table = pd.merge(Final_table, c, how = 'left', left_on = 'Country Transferred', right_on = 'Label')
Final_table.columns = ['Foreign geography' if x=='Notation' else x for x in Final_table.columns]

Final_table['Dublin Regulation Article'] = Final_table['Dublin Regulation Article'].map(
    lambda x: {
        'Total arrivals into the UK ':'total',
        'Arrivals into UK: article 8.1 ':'article-8-1',
        'Arrivals into UK: article 8.2':'article-8-2',
        'Arrivals into UK: article 9':'article-9',
        'Arrivals into UK: article 10':'article-10',
        'Arrivals into UK: article 11':'article-11',
        'Arrivals into UK: article 12':'article-12',
        'Arrivals into UK: article 13':'article-13',
        'Arrivals into UK: article 14':'article-14',
        'Arrivals into UK: article 15':'article-15',
        'Arrivals into UK: article 16':'article-16',
        'Arrivals into UK: article 17.2':'article-17-2',
        'Arrivals into UK: article 18.1':'article-18-1',
        'Arrivals into UK: article 20.5':'article-20-5',
        'Total requests for transfers into the UK':'total',
        'Requests for transfer into UK: article 8.1':'article-8-1',
        'Requests for transfer into UK: article 8.2':'article-8-2',
        'Requests for transfer into UK: article 9':'article-9',
        'Requests for transfer into UK: article 10':'article-10',
        'Requests for transfer into UK: article 11':'article-11',
        'Request for transfer into UK: article 12':'article-12',
        'Requests for transfer into UK: article 13':'article-13',
        'Requests for transfer into UK: article 14':'article-14',
        'Requests for transfer into UK: article 15':'article-15',
        'Request for transfer into UK: article 16':'article-16',
        'Request for transfer into UK: article 17.2':'article-17-2',
        'Request for transfer into UK: article 18.1':'article-18-1',
        'Request for transfer into UK: article 20.5':'article-20-5'        
        }.get(x, x))


Final_table = Final_table[['Period','Foreign geography','Nature of Transfer','Dublin Regulation Article','Measure Type','Value','Unit']]

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


