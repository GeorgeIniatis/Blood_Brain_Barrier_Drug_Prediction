import streamlit as st
import pandas as pd
import base64


# Reference
# https://discuss.streamlit.io/t/include-svg-image-as-part-of-markdown/1314
def render_svg(svg_file):
    with open(svg_file, "r") as f:
        lines = f.readlines()
        svg = "".join(lines)

        """Renders the given svg string."""
        b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
        html = r'<img src="data:image/svg+xml;base64,%s"/>' % b64
        return html


def app():
    dataset = st.container()
    creation_process = st.container()

    with dataset:
        st.subheader("Dataset")
        dataset = pd.read_excel("Streamlit_App/data/Datasets/Dataset.xlsx")
        dataset = dataset.astype(str)
        st.write(dataset.head(10))

        st.subheader("Counts")
        st.markdown(f"- Total entries: {dataset.count()[0]}  \n"
                    f"- Entries with LogBB Available: {dataset[dataset['logBB'] != '-'].count()[0]}  \n"
                    f"- Entries with Side Effects and Indications Available: {dataset[dataset['Side_Effects'] != '-'].count()[0]}  \n"
                    f"- BBB+ count: {dataset[dataset['Class'] == '1'].count()[0]}  \n"
                    f"- BBB- count: {dataset[dataset['Class'] == '0'].count()[0]}")

        st.subheader("Principal Component Analysis")
        st.markdown(render_svg("Streamlit_App/data/Plots/pca.svg"), unsafe_allow_html=True)

    with creation_process:
        st.subheader("Creation Process")
        st.markdown(
            """
            - Started with the [Singh et al.](https://www.sciencedirect.com/science/article/pii/S1093326319303547) dataset and added on top of it the [Zhao et al](https://pubs.acs.org/doi/10.1021/ci600312d), [Gao et al](https://academic.oup.com/bioinformatics/article/33/6/901/2623044), [Zhang et al](https://link.springer.com/article/10.1007%2Fs11095-008-9609-0) datasets
               - All columns were removed except the ones with the SMILES format, drug Name, experimental logBB value and BBB permeability (Class)
               - When the experimental logBB was available, BBB permeability was recalculated based on the threshold suggested by [Li et al.](https://pubs.acs.org/doi/10.1021/ci050135u) (BBB+ if LogBB >= -1)
               - When SMILES was available it was used to retrieve the PubChem_CID, MW, TPSA, xLogP, NHD, NHA, NRB, Synonyms and the drug Name (Essentially the first synonym) using the PubChem API
               - When SMILES wasn't available but the drug Name was, it was used to retrieve the PubChem_CID and SMILES format and then from there all the mentioned descriptors and variables were retrieved
               - Once the synonyms were retrieved for a specific drug or compound they were looked up in the SIDER dataset. If a synonym was found in the SIDER dataset we retrieved the SIDER_CID and the associated Side_Effects and Indications. Decided to only use the PT (Preferred Term) side effects and indications to make everything simpler. The LLT (Lowest Level Term) side effects are taken from labels of drugs but they can be too complicated. Multiple LLTs can be simplified using a single PT
            - Used [PubMed's E-Utilities API](https://www.ncbi.nlm.nih.gov/books/NBK25501/) to get abstracts from PubMed and academic papers from PubMed Central that matched multiple queries pointing to a negative brain permeability, in an effort to reduce the class imbalance discovered early on.
               - The various paragraphs of abstracts and academic papers were extracted using XML parsing
               - The sentences were then extracted and multiple regular expressions were used to find matches
               - Matches were then loaded into excel files and manually verified
               - The resulting excel files produced from these searches can be found on the repo
               - PubMed API searches produced 15, manually verified, compounds and drugs (14 BBB-, 1 BBB+) from 35 matches
               - PubMed Central API searches produced 91, manually verified, compounds and drugs (91 BBB-) from 361 matches
            - Used [Springer Nature's API](https://dev.springernature.com/) to get abstracts, articles and journals and followed the same process
               - Springer Meta V2 API searches produced 42, manually verified, compounds and drugs (41 BBB-, 1 BBB+) from 108 matches
               - Springer Open access API searches produced 109, manually verified, compounds and drugs (106 BBB-, 3 BBB+) from 491 matches
            - Duplicates, unknown compounds and compounds without all chemical descriptors available were removed
            - Compounds and drugs that returned multiple PubChem_CIDs and SMILES were removed
            - The DOI of each academic paper was provided as source for compounds and drugs. When it wasn't available either a link to PubMed or PubMed Central was provided as the source
            - The dataset was sorted based on drug name
            - Dataset before removing any duplicates or unknown compounds was 3748 compounds and drugs
            - Dataset after removing duplicates and unknown compound is currently at 2396 compounds and drugs
               - 1751 BBB+
               - 645 BBB-
               - 345 entries having side effects and indications
            - Noticed diminishing returns trend with each dataset added. Only a small number of new compounds and drugs were discovered
            """)
