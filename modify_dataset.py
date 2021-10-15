import pandas as pd
import numpy as np
import requests

pd.set_option('display.max_columns', None)

excelFile = 'Dataset.xlsx'
worksheet = 'Whole Set'

whole_set = pd.read_excel(excelFile, worksheet)

# Needed to avoid string to float errors associated with NaN
whole_set.fillna({
    'Name_Found': '',
    'Compound_CID': '',
    'logP': '',
    'NHD': '',
    'NHA': '',
    'pka(Acid)': '',
    'pka(Base)': '',
    'NRB': '',
    'Synonyms': '',
}, inplace=True)

print(whole_set.shape)

whole_set['Class'] = np.where(whole_set['logBB'] >= -1, 1, 0)

BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/"

for index, row in whole_set.iterrows():
    dataset_SMILES = row['SMILES']
    dataset_MW = row['MW']

    # Get CID
    response = requests.get(BASE + f"smiles/{dataset_SMILES}/cids/txt")
    if response:
        cid = response.json()

        # Get Synonyms & Name
        response = requests.get(BASE + f"cid/{cid}/synonyms/json")
        # Some compounds don't have any synonyms
        if response:
            synonyms = response.json()['InformationList']['Information'][0]['Synonym']
            name = synonyms[0]
        else:
            synonyms = '-'
            name = '-'
    else:
        cid = '-'
        synonyms = '-'
        name = '-'

    whole_set.at[index, 'Compound_CID'] = cid
    whole_set.at[index, 'Name_Found'] = name
    whole_set.at[index, 'Synonyms'] = synonyms

    # Get MW
    #response = requests.get(BASE + f"cid/{cid}/property/MolecularWeight/txt")
    #if response:
    #    mw = response.json()
    #else:
    #    mw = '-'

    print(index)

whole_set.to_excel('Dataset_New.xlsx')

