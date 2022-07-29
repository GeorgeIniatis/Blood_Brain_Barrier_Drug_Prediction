import streamlit as st


def app():
    references = st.container()

    with references:
        st.subheader("Libraries")
        st.markdown("""
                    - [Streamlit](https://streamlit.io/)
                    - [Scikit-Learn](https://scikit-learn.org/stable/)
                    - [Numpy](https://numpy.org/)
                    - [Pandas](https://pandas.pydata.org/)
                    - [Plotly](https://plotly.com/)
                    - [ELI5](https://eli5.readthedocs.io/en/latest/overview.html)
                    - [LIME](https://lime-ml.readthedocs.io/en/latest/)
                    """)

        st.subheader("APIs")
        st.markdown("""
                    - [PubMed's E-Utilities API](https://www.ncbi.nlm.nih.gov/books/NBK25501/)
                    - [Springer Nature's API](https://dev.springernature.com/)
                    """)

        st.subheader("Data Sources")
        st.markdown("""
                    - [SIDER Database](http://sideeffects.embl.de/) (Drug Side-Effects and Indications)
                    - [Singh et al](https://www.sciencedirect.com/science/article/pii/S1093326319303547) (A classification model for blood brain barrier penetration)
                    - [Saber et al](https://www.researchsquare.com/article/rs-29117/v1) (A machine learning model for the prediction of drug permeability across the Blood-Brain Barrier: a comparative approach)
                    - [Zhao et al](https://pubs.acs.org/doi/10.1021/ci600312d) (Predicting Penetration Across the Blood-Brain Barrier from Simple Descriptors and Fragmentation Schemes)
                    - [Gao et al](https://academic.oup.com/bioinformatics/article/33/6/901/2623044) (Predict drug permeability to blood–brain-barrier from clinical phenotypes drug side effects and drug indications)
                    - [Zhang et al](https://link.springer.com/article/10.1007%2Fs11095-008-9609-0) (QSAR Modelling of the Blood–Brain Barrier Permeability for Diverse Organic Compounds)
                    """)

        st.subheader("Tutorials")
        st.markdown(
            """
            - [Misra Turp's Streamlit Playlist](https://www.youtube.com/watch?v=-IM3531b1XU&list=PLM8lYG2MzHmTATqBUZCQW9w816ndU0xHc&ab_channel=M%C4%B1sraTurp)
            - [Prakhar Rathi's Article on Multi Page Streamlit Applications](https://towardsdatascience.com/creating-multipage-applications-using-streamlit-efficiently-b58a58134030)
            - [Renu Khandelwal's Article on LIME](https://towardsdatascience.com/developing-trust-in-machine-learning-models-predictions-e49b0064abab)
            """
        )
