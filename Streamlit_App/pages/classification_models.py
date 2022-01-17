import streamlit as st
import pandas as pd
from joblib import load

cd_model_name_to_file = {
    '-': '-',
    'Dummy Classifier': 'dc_cd.joblib',
    'Logistic Regression': 'optimised_lr_cd.joblib',
    'Support Vector Classification': 'optimised_svc_cd.joblib',
    'K-Nearest Neighbour Classifier': 'optimised_knnc_cd.joblib',
    'Random Forest Classifier': 'optimised_rfc_cd.joblib',
    'Decision Tree Classifier': 'optimised_dtc_cd.joblib',
    'Stochastic Gradient Descent Classifier': 'optimised_sgdc_cd.joblib',
}


def app():
    useful_info = st.container()
    cd_models = st.container()
    cd_chosen_model_and_inputs, cd_prediction_metrics = st.columns(2)
    cd_se_i_models = st.container()

    with useful_info:
        st.subheader("Classification Models")
        st.markdown("""
                    - Classification models make use of the Class as the label
                    - All models were optimised for F1 score using a 10-Fold Cross Validation except for the case of the Dummy Classifier
                    - Two different model categories:
                       - Category 1: Models with just the Chemical Descriptors used as features
                       - Category 2: Models with Chemical Descriptors, Side Effects and Indications used as features
                    - Training sets:
                        - For category 1 the whole dataset will be used, excluding the entries used in the Test set
                        - For category 2 a subset of the dataset will be used, those entries that have Side Effects and Indications available, again excluding the entries used in the Test set
                    - Test set:
                        - Will be used to compare the models against against each other
                        - 20% subset of the dataset entries that have Chemical Descriptors and Side Effects and Indicators. This is to allow us to use compare the performance of the two different categories of models using the same test set
                    """)

    with cd_models:
        st.subheader("Category 1: Models with just the Chemical Descriptors used as features")

        st.markdown("##### Training Performance")
        training_performance_cd = pd.read_excel("data/Metrics/Classification_Models_CD_Training_Metrics.xlsx",
                                                skiprows=1)
        training_performance_cd = training_performance_cd.round(5)
        training_performance_cd = training_performance_cd.astype(str)
        st.table(training_performance_cd)

        st.markdown("##### Testing Performance")
        testing_performance_cd = pd.read_excel("data/Metrics/Classification_Models_CD_Testing_Metrics.xlsx", skiprows=1)
        testing_performance_cd = testing_performance_cd.round(5)
        testing_performance_cd = testing_performance_cd.astype(str)
        st.table(testing_performance_cd)

        with cd_chosen_model_and_inputs:
            st.markdown("##### Make Predictions")
            cd_chosen_model = st.selectbox('Please choose a model to make predictions', cd_model_name_to_file.keys())
            if cd_chosen_model != "-":
                mw = st.number_input("Molecular Weight (MW)", min_value=0.0)
                tpsa = st.number_input("Topological Polar Surface Area (TPSA)", min_value=0.0)
                xlogp = st.number_input("XLogP3-AA (XLogP)", min_value=0.0)
                nhd = st.number_input("Hydrogen Bond Donor Count (NHD)", min_value=0.0)
                nha = st.number_input("Hydrogen Bond Acceptor Count (NHA)", min_value=0.0)
                nrb = st.number_input("Rotatable Bond Count (NRB)", min_value=0.0)

                if st.button("Predict"):
                    with cd_prediction_metrics:
                        st.markdown("##### Result")

                        model = load(
                            f"data/Classification_Models/CD/{cd_model_name_to_file[cd_chosen_model]}")
                        user_inputs = pd.DataFrame([[mw, tpsa, xlogp, nhd, nha, nrb]],
                                                   columns=['MW', 'TPSA', 'XLogP', 'NHD', 'NHA', 'NRB'])

                        if cd_chosen_model not in ["Support Vector Classification",
                                                   "Stochastic Gradient Descent Classifier"]:
                            prediction_probability = model.predict_proba(user_inputs)
                            st.markdown(
                                f"Probability that it cannot enter the brain: **{prediction_probability[0][0]}**")
                            st.markdown(f"Probability that it can enter the brain: **{prediction_probability[0][1]}**")

                        prediction = model.predict(user_inputs)
                        if prediction == 1:
                            st.markdown("""
                                        The model has predicted that the compound/drug with the specific chemical properties you have specified **Can cross the BBB**
                                        """)
                        else:
                            st.markdown("""
                                        The model has predicted that the compound/drug with the specific chemical properties you have specified **Cannot cross the BBB**
                                        """)

    with cd_se_i_models:
        st.subheader("Category 2: Models with Chemical Descriptors, Side Effects and Indications used as features")

        st.markdown("##### Training Performance")
        training_performance_cd_se_i = pd.read_excel("data/Metrics/Classification_Models_CD_SE_I_Training_Metrics.xlsx",
                                                     skiprows=1)
        training_performance_cd_se_i = training_performance_cd_se_i.round(5)
        training_performance_cd_se_i = training_performance_cd_se_i.astype(str)
        st.table(training_performance_cd_se_i)

        st.markdown("##### Testing Performance")
        testing_performance_cd_se_i = pd.read_excel("data/Metrics/Classification_Models_CD_SE_I_Testing_Metrics.xlsx",
                                                    skiprows=1)
        testing_performance_cd_se_i = testing_performance_cd_se_i.round(5)
        testing_performance_cd_se_i = testing_performance_cd_se_i.astype(str)
        st.table(testing_performance_cd_se_i)
