from modify_dataset import *
from config import *
import xml.etree.ElementTree as ET
import re

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
api_key = PUBMED_API_KEY

regular_expressions = [
    ".*was not able to cross the blood.brain barrier.*",
    ".*was not able to cross the bbb.*",
    ".*was not able to penetrate the blood.brain barrier.*",
    ".*was not able to not penetrate the bbb.*",
    ".*was not able to pass through the blood.brain barrier.*",
    ".*was not able tp pass through the bbb.*",
    ".*was not able to get through the blood.brain barrier.*",
    ".*was not able to get through the bbb.*",

    ".*does not cross the blood.brain barrier.*",
    ".*does not cross the bbb.*",
    ".*does not penetrate the blood.brain barrier.*",
    ".*does not penetrate the bbb.*",
    ".*does not pass through the blood.brain barrier.*",
    ".*does not pass through the bbb.*",
    ".*does not get through the blood.brain barrier.*",
    ".*does not get through the bbb.*",

    ".*inability to cross the blood.brain barrier.*",
    ".*inability to cross the bbb.*",
    ".*inability to penetrate the blood.brain barrier.*",
    ".*inability to penetrate the bbb.*",
    ".*inability to pass through the blood.brain barrier.*",
    ".*inability to pass through the bbb.*",
    ".*inability to get through the blood.brain barrier.*",
    ".*inability to get through the bbb.*",

    ".*unable to cross the blood.brain barrier.*",
    ".*unable to cross the bbb.*",
    ".*unable to penetrate the blood.brain barrier.*",
    ".*unable to penetrate the bbb.*",
    ".*unable to pass through the blood.brain barrier.*",
    ".*unable to pass through the bbb.*",
    ".*unable to get through the blood.brain barrier.*",
    ".*unable to get through the bbb.*",
]


def raw_string(string):
    return fr"{string}"


def get_uids(database, query, max_number):
    query_encoded = quote(query, safe='')
    response = requests.get(
        BASE + f"esearch.fcgi?db={database}&term={query_encoded}&retmax={max_number}&api_key={api_key}")
    if response.status_code == 200:
        xml_string = response.text
        xml = ET.fromstring(xml_string)
        return [uid_event.text for uid_event in xml.find("IdList").findall("Id")]


# pubmed works
# check pmc
def get_doi(database, uid):
    response = requests.get(BASE + f"efetch.fcgi?db={database}&id={uid}&rettype=xml&api_key={api_key}")
    if response.status_code == 200:
        xml_string = response.text
        xml = ET.fromstring(xml_string)

        if database == "pubmed":
            try:
                doi = xml.find("PubmedArticle").find("MedlineCitation").find("Article").find(
                    "ELocationID[@EIdType='doi']").text

            except AttributeError:
                try:
                    doi = xml.find("PubmedArticle").find("PubmedData").find("ArticleIdList").find(
                        "ArticleId[@IdType='doi']").text
                except AttributeError:
                    doi = "-"

        elif database == "pmc":
            try:
                doi = xml.find("article").find("front").find("article-meta").find("article-id[@pub-id-type='doi']").text

            except AttributeError:
                doi = "-"

        return doi


def perform_searches(database, uids_list):
    matches_lists = []
    index = 0

    for uid in uids_list:
        response = requests.get(BASE + f"efetch.fcgi?db={database}&id={uid}&rettype=xml&api_key={api_key}")
        if response.status_code == 200:
            xml_string = response.text
            xml = ET.fromstring(xml_string)

            if database == "pubmed":
                try:
                    abstract_texts = [''.join(abstract_text.itertext()) for abstract_text in
                                      xml.find("PubmedArticle").find("MedlineCitation").find("Article").find(
                                          "Abstract").findall("AbstractText")]
                    for abstract_text in abstract_texts:
                        sentences = abstract_text.split(".")
                        for sentence in sentences:
                            for regular_expression in regular_expressions:
                                matches = re.findall(raw_string(regular_expression), sentence)
                                if matches:
                                    print("Matches found")
                                    source = get_doi(database, uid)
                                    if source != '-':
                                        source = "https://doi.org/" + source
                                    for match in matches:
                                        matches_lists.append([uid, source, database, regular_expression, match])
                except AttributeError:
                    print("No abstract")
                    continue

            elif database == "pmc":
                try:
                    section_elements = xml.find("article").find("body").findall("sec")
                    for section_element in section_elements:
                        paragraphs = [''.join(paragraph_element.itertext()) for paragraph_element in
                                      section_element.findall("p")]

                        subsection_elements = section_element.findall("sec")
                        if subsection_elements:
                            for subsection_element in subsection_elements:
                                subsection_paragraphs = [''.join(subsection_paragraph_element.itertext()) for
                                                         subsection_paragraph_element in
                                                         subsection_element.findall("p")]
                                paragraphs += subsection_paragraphs

                        for paragraph in paragraphs:
                            sentences = paragraph.split(".")
                            for sentence in sentences:
                                for regular_expression in regular_expressions:
                                    matches = re.findall(raw_string(regular_expression), sentence)
                                    if matches:
                                        print("Matches found")
                                        source = get_doi(database, uid)
                                        if source != '-':
                                            source = "https://doi.org/" + source
                                        for match in matches:
                                            matches_lists.append([uid, source, database, regular_expression, match])
                except AttributeError:
                    print("No body")
                    continue

        print(index)
        index += 1

    return matches_lists


def create_dataframe_and_load_to_excel(matches_lists, new_file_name):
    dataframe = pd.DataFrame(matches_lists,
                             columns=['UID', 'Source', 'Database', 'Regular_Expression', 'Match'])

    load_to_excel(dataframe, new_file_name)


if __name__ == "__main__":
    database_options = ["pubmed", "pmc"]
    query = "blood brain barrier permeability"

    # pubmed_uids_list = get_uids(database_options[0], query, 15000)
    # matches_lists = perform_searches(database_options[0], pubmed_uids_list)
    # create_dataframe_and_load_to_excel(matches_lists, "PubMed_Searches.xlsx")

    '''working_set = load_from_excel("PubMed_Central_Searches.xlsx", "Sheet1")
    working_set["Source"] = ""

    for index, row in working_set.iterrows():
        pmcid = row["PMCID"]
        source = get_doi(database_options[1], pmcid)
        if source != '-':
            source = "https://doi.org/" + source
        print(index)

        working_set.at[index, 'Source'] = source

    load_to_excel(working_set, "PubMed_Central_Searches_Sources.xlsx")'''



    # pmc_uids_list = get_uids(database_options[1], query, 80000)
    # matches_lists = perform_searches(database_options[1], pmc_uids_list)
    # create_dataframe_and_load_to_excel(matches_lists, "PubMed_Central_Searches.xlsx")
