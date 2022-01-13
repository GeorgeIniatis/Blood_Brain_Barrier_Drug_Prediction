import streamlit as st


def app():
    project_introduction = st.container()
    dataset = st.container()

    with project_introduction:
        st.subheader("Introduction")
        st.markdown(
            "The brain is surrounded by a permeable boundary that prevents many pathogens from getting in, however, "
            "it can also stop many useful drugs from entering the brain. This is especially important when trying to "
            "deliver critical therapeutics, such as chemotherapy, to brain tumours. Accurate prediction of whether a "
            "drug will easily cross the blood-brain barrier is a valuable tool for developing and testing new drugs "
            "for various diseases.")
        st.markdown(
            "**Original Aims**: This project aimed to gather publicly available data on drugs known to cross into the brain and those "
            "that cannot and place them into a new dataset and then using that new dataset train machine learning models"
            "that use a drug's or compound's chemical descriptors to predict whether it can pass into the brain or not")

        st.markdown("**Actual Achievements**: ....")

    with dataset:
        st.header("Dataset")
