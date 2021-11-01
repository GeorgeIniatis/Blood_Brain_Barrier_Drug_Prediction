import urllib.error
import urllib3.exceptions
from modify_dataset import *
from googlesearch import search
import re

'''
Might need a VPN service to run. Connecting to Marseille seems to be working really well for me
HTTP Error 429: Too Many Requests is extremely common
'''

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
}

queries_and_regular_expressions = [
    ["\"does not cross the blood-brain barrier\"", "\w+.\w+.\w+.does not cross the blood.brain barrier."],
    ["\"does not pass through the blood-brain barrier\"", "\w+.\w+.\w+.does not pass through the blood.brain barrier."],
    ["\"cannot get through the blood-brain barrier\"", "\w+.\w+.\w+.cannot get through the blood.brain barrier."],
    ["\"cannot cross the blood-brain barrier\"", "\w+.\w+.\w+.cannot cross the blood.brain barrier."],
    ["\"does not cross the BBB\"", "\w+.\w+.\w+.does not cross the bbb."],
    ["\"does not pass through the BBB\"", "\w+.\w+.\w+.does not pass through the bbb."],
    ["\"cannot get through the BBB\"", "\w+.\w+.\w+.cannot get through the bbb."],
    ["\"cannot cross the BBB\"", "\w+.\w+.\w+.cannot cross the bbb."],
    ["\"cannot penetrate the blood-brain barrier\"", "\w+.\w+.\w+.cannot penetrate the blood.brain barrier."],
    ["\"cannot penetrate the BBB\"", "\w+.\w+.\w+.cannot penetrate the bbb."],
]

search_sites = ["https://pubs.acs.org/", "https://pubmed.ncbi.nlm.nih.gov/", "https://www.ncbi.nlm.nih.gov/pmc/"]


def raw_string(string):
    return fr"{string}"


# returns a list of lists
# [ ["Query", "Regular expression used to get matches", "Actual matched string", "URL"] , [...] ]
def automated_google_searches(query_and_regular_expression):
    potential_drugs = []
    index = 0

    try:
        for search_site in search_sites:
            query = query_and_regular_expression[0] + f" site:{search_site}"
            regular_expression = query_and_regular_expression[1]

            for url in search(query, tld="com", lang='en', num=100, start=0, stop=None, pause=3.0):
                print(f"Query: {query}")
                print(f"URL: {url}")
                try:
                    request = requests.get(url, headers=headers, timeout=10)
                    if request.status_code == 200:
                        try:
                            page_content = request.text.lower()
                            page_content_size = len(page_content)
                            print(f"Content size: {page_content_size}")
                            match = re.search(raw_string(regular_expression), page_content)
                            if match is not None:
                                print("Match found")
                                potential_drugs.append([query, regular_expression, match.group(0), url])
                            else:
                                print("Match not found")

                        except MemoryError:
                            print("Memory error!")
                            continue
                except requests.exceptions.RequestException as e:
                    print(e)
                    print()
                    continue
                except urllib3.exceptions.LocationParseError as e:
                    print(e)
                    print()
                    continue

                print(index)
                print()
                index += 1
    except urllib.error.HTTPError as e:
        print(e)

    return potential_drugs


def create_dataframe_and_load_to_excel(potential_drugs, new_file_name):
    dataframe = pd.DataFrame(potential_drugs,
                             columns=['Query', 'Regular_Expression', 'Matched_String', 'URL'])

    load_to_excel(dataframe, new_file_name)


if __name__ == "__main__":
    '''index = 1
    for query_and_regular_expression in queries_and_regular_expressions[0:]:
        potential_drugs_dictionary = automated_google_searches(query_and_regular_expression)
        create_dataframe_and_load_to_excel(potential_drugs_dictionary, f'Google_Searches_Subset_{index}.xlsx')
        index += 1'''

    index = 10
    potential_drugs_dictionary = automated_google_searches(queries_and_regular_expressions[9])
    create_dataframe_and_load_to_excel(potential_drugs_dictionary, f'Google_Searches_Subset_{index}.xlsx')
