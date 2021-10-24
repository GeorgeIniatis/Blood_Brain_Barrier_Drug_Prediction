from modify_dataset import *
from googlesearch import search
from urllib.parse import urlparse
import re

'''
Might need a VPN service to run. Connecting to Marseille seems to be working really well for me
HTTP Error 429: Too Many Requests is extremely common
'''


def raw_string(string):
    return fr"{string}"


queries = [["\"does not cross the blood-brain barrier\"", '\w+ does not cross the \w+.\w+.\w+'],
           ["\"does not cross the BBB\"", '\w+ does not cross the BBB'],
           ["\"doesn't cross the blood-brain barrier\"", '\w+ doesn\'t cross the \w+.\w+.\w+'],
           ["\"doesn't cross the BBB\"", '\w+ does\'t cross the BBB']]

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

# Causing memory errors
domain_black_list = ['nursing.ceconnection.com']

index = 0
for query in queries:
    for url in search(query[0], tld="com", lang='en', num=100, start=0, stop=None, pause=2.0):
        domain = urlparse(url).netloc
        print(domain)
        if domain not in domain_black_list:
            try:
                request = requests.get(url, headers=headers, timeout=10)
                if request.status_code == 200:
                    page_content = request.text
                    matches = re.findall(raw_string(query[1]), page_content)

                    for match in matches:
                        potential_drug_name = match.split(' ')[0].lower()
                        potential_drugs[potential_drug_name] = [query[0], query[1], match, url]
            except requests.exceptions.RequestException as e:
                print(e)
                continue

        print(index)
        index += 1

data = []
for key, value in potential_drugs.items():
    pubchem_cid_smiles = get_pubchem_cid_and_smiles_using_name(key)
    if pubchem_cid_smiles is not None:
        data.append([pubchem_cid_smiles[1], pubchem_cid_smiles[0], key, value[0], value[1], value[2], value[3], 0])

dataframe = pd.DataFrame(data,
                         columns=['SMILES', 'PubChem_CID', 'Name', 'Query', 'Regular_Expression', 'Matched_String',
                                  'URL', 'Class'])
load_to_excel(dataframe, 'Google_Searches.xlsx')
