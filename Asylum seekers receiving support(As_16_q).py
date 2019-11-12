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

# Table as_16_q: Asylum seekers in receipt of Section 95 support, by local authority, as at end of quarter

# +
from gssutils import *

scraper = Scraper('https://www.gov.uk/government/statistics/immigration-statistics-october-to-december-2017-data-tables')
scraper
# -

dist = scraper.distribution(
    title='Asylum data tables immigration statistics October to December 2017 volume 4'
)
sheets = dist.as_pandas()
sheets.keys()

# Metadata is in the spreadsheet 'Contents' tab.

# +
TAB_NAME = 'as_16_q'

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

observations = sheets[TAB_NAME].iloc[3:, :7].copy()
observations.rename(columns= observations.iloc[0], inplace=True)
observations.drop(observations.index[0], inplace = True)
observations.drop('Region', axis = 1, inplace = True)
Final_table = pd.melt(observations,
                       ['Quarter','Local Authority'],
                       var_name="Total supported under Section 95",
                       value_name="Value")
Final_table.Value.dropna(inplace =True)
Final_table['Unit'] = 'asylum-seekers'
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
Final_table.rename(columns={'Total supported under Section 95': 'Section 95 Support'}, inplace=True)
Final_table['Period'] = Final_table['Period'].astype(str)
Final_table = Final_table[Final_table['Period'] != '']
Final_table['Period'] = 'quarter/' + Final_table['Period'].map(lambda cell: cell.replace(' ','-'))
Final_table['Section 95 Support'] = Final_table['Section 95 Support'].map(lambda cell: cell.replace('In receipt of subsistence \nonly', 'In receipt of subsistence only'))

Final_table['Local Authority'] = Final_table['Local Authority'].str.lstrip('*')

Final_table['Local Authority'] = Final_table['Local Authority'].map(
    lambda x: {
        'Total East Midlands':'East Midlands',
        'Total East of England':'East of England',
        'Total London':'London',
        'Total North East':'North East',
        'Total North West':'North West',
        'Total Northern Ireland':'Northern Ireland',
        'Total Scotland':'Scotland',
        'Total South East':'South East',
        'Total South West':'South West',
        'Total Wales':'Wales',
        'Total West Midlands':'West Midlands',
        'Total Yorkshire and The Humber':'Yorkshire and The Humber',
        'Total England' : 'England',
        'Total Other and Unknown' : 'Other and Unknown'
        }.get(x, x))

Final_table['Section 95 Support'] = Final_table['Section 95 Support'].map(
    lambda x: {
        'Total supported under Section 95':'total-supported',
        'In receipt of subsistence only':'subsistence-only',
        'In dispersed accommodation':'dispersed-accommodation',
        'Disbenefited':'disbenefited',
        }.get(x, x))

# Take the Labels:Codes pairs from ./gss-codes.csv and create a dictionary
# use that to convert 'Local Authority' labels to codes
lookup_dict = {}
name_to_label_dataframe = pd.read_csv("./gss-codes.csv")
for _, row in name_to_label_dataframe.iterrows():
    lookup_dict.update({row["Label"]: row["Code"]})
Final_table["Local Authority"] = Final_table["Local Authority"].map(lambda x: lookup_dict[x])
Final_table.rename(columns={'Local Authority':'Geography'}, inplace=True)

Final_table = Final_table[['Period','Geography','Section 95 Support','Measure Type','Value','Unit']]

# Remove 3 and 4 digit geography codes are they are obsolete after 2015 and not on the Geography website causing the pipeline to fail
# Also removed 'other-and-unkown for smae reason'
Final_table = Final_table[(Final_table['Geography'].str.len() > 5) & (Final_table['Geography'] != "other-and-unknown")]
#Final_table["Geography"].unique()

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


