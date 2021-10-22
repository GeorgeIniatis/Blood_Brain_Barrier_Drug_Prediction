from modify_dataset import *
from googlesearch import search
from urllib.parse import urlparse
import re

# search(query, tld='com', lang='en', num=10, start=0, stop=None, pause=2.0)
query = "\"does not cross the blood-brain barrier\""
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
}

potential_drugs = {}

domain_white_list = ['pubmed.ncbi.nlm.nih.gov', 'diabetes.diabetesjournals.org', 'bmcneurosci.biomedcentral.com',
                     'thejournalofheadacheandpain.biomedcentral.com', 'academic.oup.com', 'www.nature.com',
                     'www.researchgate.net', 'www.asaabstracts.com', 'www.jneurosci.org', 'onlinelibrary.wiley.com',
                     'tspace.library.utoronto.ca', 'www.hindawi.com', 'jpet.aspetjournals.org', 'psycnet.apa.org',
                     'cancerres.aacrjournals.org', 'benthamscience.com', 'www.pnas.org', 'pubs.acs.org',
                     'www.karger.com', 'ascopubs.org', 'research-information.bris.ac.uk', 'www.sec.gov',
                     'www.redjournal.org', 'www.ahajournals.org', 'www.mdedge.com', 'n.neurology.org',
                     'www.alzforum.org', 'core.ac.uk', 'www.northeastern.edu',
                     'sites.duke.edu', 'scientiaricerca.com', 'www.statpearls.com', 'www.chemdiv.com',
                     'www.medscape.org', 'www.rch.org.au',
                     'www.apdaparkinson.org', 'www.bbrfoundation.org', 'www.rockefeller.edu', 'www.academia.edu',
                     'en.wikipedia.org', 'www.cureus.com', 'uofuhealth.utah.edu']

for url in search(query, tld="com", lang='en', num=1000, stop=1000, pause=2):
    domain = urlparse(url).netloc
    if domain in domain_white_list:
        request = requests.get(url, headers=headers, timeout=10)
        if request.status_code == 200:
            page_content = request.text
            matches = re.findall(r'\w+ does not cross the \w+.\w+.\w+', page_content)

            for match in matches:
                potential_drug_name = match.split(' ')[0].lower()
                potential_drugs[potential_drug_name] = [match, url]

data = []
for key, value in potential_drugs.items():
    pubchem_cid_smiles = get_pubchem_cid_and_smiles_using_name(key)
    print(pubchem_cid_smiles)
    if (pubchem_cid_smiles is not None) and (len(pubchem_cid_smiles) == 2):
        data.append([pubchem_cid_smiles[1], pubchem_cid_smiles[0], key, value[0], value[1], 0])

dataframe = pd.DataFrame(data, columns=['SMILES', 'PubChem_CID', 'Name', 'Matched_String', 'URL', 'Class'])
load_to_excel(dataframe, 'Google_Searches.xlsx')
