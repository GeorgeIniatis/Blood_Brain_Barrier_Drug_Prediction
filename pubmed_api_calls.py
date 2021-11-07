from modify_dataset import *
from config import PUBMED_API_KEY
import xml.etree.ElementTree as ET
import re

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

regular_expressions = [
    ".*was not able to cross the blood.brain barrier.*",
    ".*was not able to cross the bbb.*",
    ".*was not able to penetrate the blood.brain barrier.*",
    ".*was not able to not penetrate the bbb.*",
    ".*was not able to pass through the blood.brain barrier.*",
    ".*was not able to pass through the bbb.*",
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
        BASE + f"esearch.fcgi?db={database}&term={query_encoded}&retmax={max_number}&api_key={PUBMED_API_KEY}")
    if response.status_code == 200:
        xml_string = response.text
        xml = ET.fromstring(xml_string)
        return [uid_event.text for uid_event in xml.find("IdList").findall("Id")]


def get_doi(database, xml):
    if database == "pubmed":
        try:
            return xml.find("PubmedArticle").find("MedlineCitation").find("Article").find(
                "ELocationID[@EIdType='doi']").text
        except AttributeError:
            try:
                return xml.find("PubmedArticle").find("PubmedData").find("ArticleIdList").find(
                    "ArticleId[@IdType='doi']").text
            except AttributeError:
                return "-"

    elif database == "pmc":
        try:
            return xml.find("article").find("front").find("article-meta").find(
                "article-id[@pub-id-type='doi']").text
        except AttributeError:
            return "-"
    else:
        return None


# Splits the paragraphs into sentences and for each sentence the regular expressions are used to find matches
def search_for_matches(database, xml, uid, paragraphs):
    temp_list = []
    for paragraph in paragraphs:
        sentences = paragraph.split(".")
        for sentence in sentences:
            for regular_expression in regular_expressions:
                matches = re.findall(raw_string(regular_expression), sentence)
                if matches:
                    print("Matches found")
                    source = get_doi(database, xml)
                    if (source is not None) and (source != '-'):
                        source = "https://doi.org/" + source
                    for match in matches:
                        temp_list.append([uid, source, database, regular_expression, match])

    return temp_list


def perform_searches(database, uids_list):
    matches_lists = []
    index = 0

    for uid in uids_list:
        response = requests.get(BASE + f"efetch.fcgi?db={database}&id={uid}&rettype=xml&api_key={PUBMED_API_KEY}")
        if response.status_code == 200:
            xml_string = response.text
            xml = ET.fromstring(xml_string)

            if database == "pubmed":
                try:
                    abstract_texts = [''.join(abstract_text.itertext()) for abstract_text in
                                      xml.find("PubmedArticle").find("MedlineCitation").find("Article").find(
                                          "Abstract").findall("AbstractText")]

                    matches_lists += search_for_matches(database, xml, uid, abstract_texts)
                except AttributeError:
                    print("No abstract")
                    pass

            elif database == "pmc":
                try:
                    section_elements = xml.find("article").find("body").findall("sec")
                    for section_element in section_elements:
                        paragraphs = [''.join(paragraph_element.itertext()) for paragraph_element in
                                      section_element.findall("p")]

                        try:
                            subsection_elements = section_element.findall("sec")
                            for subsection_element in subsection_elements:
                                subsection_paragraphs = [''.join(subsection_paragraph_element.itertext()) for
                                                         subsection_paragraph_element in
                                                         subsection_element.findall("p")]
                                paragraphs += subsection_paragraphs
                        except AttributeError:
                            pass

                        matches_lists += search_for_matches(database, xml, uid, paragraphs)
                except AttributeError:
                    print("No body")
                    pass
                except ConnectionError:
                    print("Connection Error")
                    pass

        print(index)
        # Some backups in case of error
        if index in [10000, 20000, 30000, 40000, 50000, 60000]:
            create_dataframe_and_load_to_excel(matches_lists, f"PubMed_Central_Searches_{index}.xlsx")
        index += 1

    return matches_lists


def create_dataframe_and_load_to_excel(matches_lists, new_file_name):
    dataframe = pd.DataFrame(matches_lists,
                             columns=['UID', 'Source', 'Database', 'Regular_Expression', 'Match'])

    load_to_excel(dataframe, new_file_name)


if __name__ == "__main__":
    database_options = ["pubmed", "pmc"]
    query_string = "blood brain barrier permeability"

    # PubMed Searches
    pubmed_uids_list = get_uids(database_options[0], query_string, 15000)
    matches_lists = perform_searches(database_options[0], pubmed_uids_list)
    create_dataframe_and_load_to_excel(matches_lists, "PubMed_Searches.xlsx")

    # PMC Searches
    pmc_uids_list = get_uids(database_options[1], query_string, 80000)
    matches_lists = perform_searches(database_options[1], pmc_uids_list)
    create_dataframe_and_load_to_excel(matches_lists, "PubMed_Central_Searches.xlsx")
