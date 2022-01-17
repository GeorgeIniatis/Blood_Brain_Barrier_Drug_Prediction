import streamlit as st


def app():
    project_introduction = st.container()
    about_us = st.container()

    with project_introduction:
        st.subheader("Introduction")
        st.markdown("""
            The brain is surrounded by a permeable boundary that prevents many pathogens from getting in, however, 
            it can also stop many useful drugs from entering the brain. This is especially important when trying to 
            deliver critical therapeutics, such as chemotherapy, to brain tumours. Accurate prediction of whether a 
            drug will easily cross the blood-brain barrier is a valuable tool for developing and testing new drugs 
            for various diseases.""")
        st.markdown("""
            **Original Aims**: This project aimed to gather publicly available data on drugs known to cross into the brain and those 
            that cannot and place them into a new dataset and then using that new dataset train machine learning models
            that use a drug's or compound's chemical descriptors to predict whether it can pass into the brain or not""")
        st.markdown("""
            **Actual Achievements**: A dataset of 2396 publicly available compounds and drugs was gathered from various academic
            papers and APIs. The models built were split into two categories, Classification and Regression. Classification models
            would try to predict whether a particular compound or drug can pass the barrier and Regression models would try to predict
            the logBB value.
            
            Various models were built for both categories using the chemical descriptors of each specific compound or drug. 
            In the case of the Classification models, these were further improved by including the side effects and indications 
            of each compound or drug. Unfortunately, this could not be replicated in the case of the Regression models due to the 
            small size of the subset
            """)

    with about_us:
        st.subheader("About")
        st.markdown("""
                    - Created by George Iniatis as part of a 4th year computer science project at the University of Glasgow
                    - Supervised by [Dr. Jake Lever](https://www.gla.ac.uk/schools/computing/staff/jakelever/)
                    """)
        st.subheader("Useful Links")
        st.markdown("""
                    - [GitHub](https://github.com/GeorgeIniatis/Blood_Brain_Barrier_Drug_Prediction) 
                    - [Notebook](https://datalore.jetbrains.com/notebook/IczIzzNdfezZefWuhmeMRx/D9Y5hyorcCW5ScYTdMTeab/)
                    """)
