import urllib3.exceptions
from modify_dataset import *
from googlesearch import search
from urllib.parse import urlparse
import re

'''
Might need a VPN service to run. Connecting to Marseille seems to be working really well for me
HTTP Error 429: Too Many Requests is extremely common
'''

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
}

queries_and_regular_expressions = [
    ["\"does not cross the blood-brain barrier\"", "\w+.does not cross the blood.brain barrier."],
    ["\"doesn't cross the blood-brain barrier\"", "\w+.doesn't cross the blood.brain barrier."],
    ["\"does not cross the BBB\"", "\w+.does not cross the bbb."],
    ["\"doesn't cross the BBB\"", "\w+.doesn't cross the bbb."],
    ["\"does not pass through the blood-brain barrier\"", "\w+.does not pass through the blood.brain barrier."],
    ["\"doesn't pass through the blood-brain barrier\"", "\w+.doesn't pass through the blood.brain barrier."],
    ["\"does not pass through the BBB\"", "\w+.does not pass through the bbb."],
    ["\"doesn't pass through the BBB\"", "\w+.doesn't pass through the bbb."],
    ["\"cannot enter the brain\"", "\w+.cannot enter the brain."],
    ["\"cannot get through the blood-brain barrier\"", "\w+.cannot get through the blood.brain barrier."],
    ["\"cannot get through the BBB\"", "\w+.cannot get through the bbb."],
    ["\"cannot cross the blood-brain barrier\"", "\w+.cannot cross the blood.brain barrier."],
    ["\"cannot cross the BBB\"", "\w+.cannot cross the bbb."],
]


def raw_string(string):
    return fr"{string}"


# returns a list of lists
# [ ["Drug name", "Query", "Regular expression used to get matches", "Actual matched string", "URL", "Domain, "Class"] , [...] ]
def automated_google_searches(query_and_regular_expression):
    potential_drugs = []
    index = 0

    query = query_and_regular_expression[0]
    regular_expression = query_and_regular_expression[1]

    for url in search(query, tld="com", lang='en', num=100, start=0, stop=None, pause=3.0):
        domain = urlparse(url).netloc
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
                        potential_drug_name = match.group(0).split(' ')[0].lower()
                        potential_drugs.append(
                            [potential_drug_name, query, regular_expression, match.group(0), url, domain, 0])
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

    return potential_drugs


def create_dataframe_and_load_to_excel(potential_drugs, new_file_name):
    dataframe = pd.DataFrame(potential_drugs,
                             columns=['Name', 'Query', 'Regular_Expression', 'Matched_String', 'URL', 'Domain',
                                      'Class'])

    load_to_excel(dataframe, new_file_name)


if __name__ == "__main__":
    index = 13
    for query_and_regular_expression in queries_and_regular_expressions[12:]:
        potential_drugs_dictionary = automated_google_searches(query_and_regular_expression)
        create_dataframe_and_load_to_excel(potential_drugs_dictionary, f'Google_Searches_Subset_{index}.xlsx')
        index += 1
