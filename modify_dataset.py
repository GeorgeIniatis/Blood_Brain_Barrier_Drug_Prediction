import pandas as pd
import numpy as np
import requests

pd.set_option('display.max_columns', None)

excelFile = 'Dataset.xlsx'
worksheet = 'Whole Set'

whole_set = pd.read_excel(excelFile, worksheet)

# Needed to avoid string to float error associated with NaN
whole_set.fillna({
    'Name_Found': '',
    'Compound_CID': '',
    'MW': '',
    'PSA': '',
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


def get_cid_using_smiles(smiles):
    response = requests.get(BASE + f"smiles/{smiles}/cids/txt")
    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_cid_using_name(name):
    response = requests.get(BASE + f"name/{name}/cids/json")
    if response.status_code == 200:
        return response.json()['IdentifierList']['CID']
    else:
        return None


def get_synonyms(cid):
    response = requests.get(BASE + f"cid/{cid}/synonyms/json")
    if response.status_code == 200:
        return response.json()['InformationList']['Information'][0]['Synonym']
    else:
        return None


uncertain_compounds_indexes = []

# Try to get CID from SMILES first. If not possible try using the name
for index, row in whole_set.iterrows():
    row_SMILES = row['SMILES'].replace("#", "%23")
    cid_from_smiles = get_cid_using_smiles(row_SMILES)

    if cid_from_smiles is not None:
        cid = cid_from_smiles
        synonyms = get_synonyms(cid_from_smiles)
        if synonyms is not None:
            name = synonyms[0]
        else:
            synonyms = '-'
            name = '-'
    else:
        row_NAME = row['Name']
        cid_from_name = get_cid_using_name(row_NAME)

        if cid_from_name is not None:
            if len(cid_from_name) == 1:
                cid = cid_from_name[0]
                synonyms = get_synonyms(cid_from_smiles)
                if synonyms is not None:
                    name = synonyms[0]
                else:
                    synonyms = '-'
                    name = '-'
            else:
                cid = '-'
                synonyms = '-'
                name = '-'

                uncertain_compounds_indexes.append(index)
        else:
            cid = '-'
            synonyms = '-'
            name = '-'

    whole_set.at[index, 'Compound_CID'] = cid
    whole_set.at[index, 'Name_Found'] = name
    whole_set.at[index, 'Synonyms'] = synonyms

    print(index)

print(uncertain_compounds_indexes)

whole_set.to_excel('Dataset_New.xlsx')
