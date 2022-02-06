from modify_dataset import *
from pubmed_api_calls import regular_expressions, raw_string, ET
from config import SPRINGER_API_KEY
import re

BASE = "https://api.springernature.com/"


def get_doi(xml, object_name):
    if object_name == "book":
        try:
            return xml.find("book-part").find("book-part-meta").find("book-part-id[@book-part-id-type='doi']").text
        except AttributeError:
            try:
                return xml.find("book-meta").find("book-id[@book-id-type='doi']").text
            except AttributeError:
                return '-'

    elif object_name == "article":
        return xml.find("front").find("article-meta").find("article-id[@pub-id-type='doi']").text


def search_for_matches(xml, object_name, paragraphs):
    temp_list = []
    for paragraph in paragraphs:
        sentences = paragraph.split(".")
        for sentence in sentences:
            for regular_expression in regular_expressions:
                matches = re.findall(raw_string(regular_expression), sentence)
                if matches:
                    print("Matches found")
                    source = get_doi(xml, object_name)
                    if source != '-':
                        source = "https://doi.org/" + source
                    for match in matches:
                        temp_list.append([source, regular_expression, match])

    return temp_list


# For meta/v2 the max number of returned records is 100
# For openaccess the max number of returned records is 20
def perform_searches(api, query, index):
    list_to_return = []

    if api == "meta/v2":
        results_to_retrieve = 100
    elif api == "openaccess":
        results_to_retrieve = 20
    else:
        results_to_retrieve = None

    query_encoded = quote(query, safe='')
    response = requests.get(
        BASE + f"{api}/jats?api_key={SPRINGER_API_KEY}&q={query_encoded}&s={index}&p={results_to_retrieve}")

    if response.status_code == 200:
        xml_string = response.text
        xml = ET.fromstring(xml_string)

        books = xml.find("records").findall("book-part-wrapper")
        articles = xml.find("records").findall("article")

        for book in books:
            paragraphs = []
            try:
                abstract_elements = book.find("book-part").find("book-part-meta").findall("abstract")
                for abstract_element in abstract_elements:
                    abstract_paragraphs = [''.join(paragraph.itertext()) for paragraph in
                                           abstract_element.findall("p")]
                    paragraphs += abstract_paragraphs
            except AttributeError:
                pass

            try:
                abstract_elements = book.find("book-part").find("body").find("book-part").find(
                    "book-part-meta").findall("abstract")
                for abstract_element in abstract_elements:
                    abstract_paragraphs = [''.join(paragraph.itertext()) for paragraph in
                                           abstract_element.findall("p")]
                    paragraphs += abstract_paragraphs
            except AttributeError:
                pass

            list_to_return += search_for_matches(book, "book", paragraphs)

            print(index)
            index += 1

        for article in articles:
            paragraphs = []
            try:
                abstract_paragraphs = [''.join(paragraph.itertext()) for paragraph in
                                       article.find("front").find("article-meta").find("abstract").findall("p")]
                paragraphs += abstract_paragraphs
            except AttributeError:
                pass

            try:
                abstract_sections = article.find("front").find("article-meta").find("abstract").findall("sec")

                for abstract_section in abstract_sections:
                    section_paragraphs = [''.join(section_paragraph.itertext()) for section_paragraph in
                                          abstract_section.findall("p")]
                    paragraphs += section_paragraphs
            except AttributeError:
                pass

            try:
                body_sections = article.find("body").findall("sec")
                for body_section in body_sections:
                    section_paragraphs = [''.join(section_paragraph.itertext()) for section_paragraph in
                                          body_section.findall("p")]
                    paragraphs += section_paragraphs

                    try:
                        body_subsections = body_section.findall("sec")
                        for body_subsection in body_subsections:
                            subsection_paragraphs = [''.join(subsection_paragraph.itertext()) for subsection_paragraph
                                                     in body_subsection.findall("p")]
                            paragraphs += subsection_paragraphs
                    except AttributeError:
                        pass
            except AttributeError:
                pass

            list_to_return += search_for_matches(article, "article", paragraphs)

            print(index)
            index += 1

    return list_to_return


def create_dataframe_and_load_to_excel(matches_lists, new_file_name):
    dataframe = pd.DataFrame(matches_lists, columns=['Source', 'Regular_Expression', 'Match'])
    load_to_excel(dataframe, new_file_name)


def create_dataframe_and_load_to_csv(matches_lists, new_file_name):
    dataframe = pd.DataFrame(matches_lists, columns=['Source', 'Regular_Expression', 'Match'])
    dataframe.to_csv(f"Dataset_Files/{new_file_name}")


if __name__ == "__main__":
    api_options = ["meta/v2", "openaccess"]
    query = '"Blood-brain barrier"'

    # meta/v2 Searches
    matches_lists = []
    for i in range(0, 80000, 100):
        matches_lists += perform_searches(api_options[0], query, i)
        # Some backups in case of error
        if i in [20000, 30000, 40000, 50000, 60000, 70000, 80000]:
            create_dataframe_and_load_to_excel(matches_lists, f"Springer_meta_v2_Searches_{i}.xlsx")
    create_dataframe_and_load_to_excel(matches_lists, "Springer_meta_v2_Searches.xlsx")
    create_dataframe_and_load_to_csv(matches_lists, "Springer_meta_v2_Searches.csv")

    # openaccess Searches
    matches_lists = []
    for i in range(0, 23500, 20):
        matches_lists += perform_searches(api_options[1], query, i)
        # Some backups in case of error
        if i in [5000, 10000, 15000, 20000]:
            create_dataframe_and_load_to_excel(matches_lists, f"Springer_openaccess_Searches_{i}.xlsx")
    create_dataframe_and_load_to_excel(matches_lists, "Springer_openaccess_Searches.xlsx")
    create_dataframe_and_load_to_csv(matches_lists, "Springer_openaccess_Searches.csv")
