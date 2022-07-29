import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from joblib import load
import matplotlib.pyplot as plt
import numpy as np
import eli5
from lime.lime_tabular import LimeTabularExplainer

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

cd_se_i_model_name_to_file = {
    '-': '-',
    'Dummy Classifier': 'dc_cd_se_i.joblib',
    'Logistic Regression': 'optimised_lr_cd_se_i.joblib',
    'Support Vector Classification': 'optimised_svc_cd_se_i.joblib',
    'K-Nearest Neighbour Classifier': 'optimised_knnc_cd_se_i.joblib',
    'Random Forest Classifier': 'optimised_rfc_cd_se_i.joblib',
    'Decision Tree Classifier': 'optimised_dtc_cd_se_i.joblib',
    'Stochastic Gradient Descent Classifier': 'optimised_sgdc_cd_se_i.joblib',
}

all_feature_columns = pd.read_csv("Streamlit_App/data/Datasets/Dataset_Feature_Columns.csv")
feature_selection_support = np.load("Streamlit_App/data/feature_selection_support.npy")
feature_selection_dataframe = pd.DataFrame(all_feature_columns.loc[:, feature_selection_support].columns)

side_effects_subset = feature_selection_dataframe.loc[feature_selection_dataframe[0].str.startswith("Side_Effect")]
side_effects = side_effects_subset[0].str.replace("Side_Effect_", "")
side_effects.reset_index(drop=True, inplace=True)
side_effects.rename('Side Effects', inplace=True)

indications_subset = feature_selection_dataframe.loc[feature_selection_dataframe[0].str.startswith("Indication")]
indications = indications_subset[0].str.replace("Indication_", "")
indications.reset_index(drop=True, inplace=True)
indications.rename('Indications', inplace=True)

X_train_cd = pd.read_csv("Streamlit_App/data/Datasets/X_train_cd.csv", index_col=0)
y_train_cd = pd.read_csv("Streamlit_App/data/Datasets/y_train_cd.csv", index_col=0)
X_train_cd_se_i = pd.read_csv("Streamlit_App/data/Datasets/X_train_cd_se_i.csv", index_col=0)
y_train_cd_se_i = pd.read_csv("Streamlit_App/data/Datasets/y_train_cd_se_i.csv", index_col=0)


def model_weights_classification(model, classification_group):
    if classification_group == 'cd':
        return eli5.format_as_dataframe(eli5.explain_weights(model,
                                                             feature_names=X_train_cd.columns,
                                                             target_names={1: "BBB+", 0: "BBB-"}))
    elif classification_group == 'cd_se_i':
        return eli5.format_as_dataframe(eli5.explain_weights(model,
                                                             feature_names=X_train_cd_se_i.loc[:,
                                                                           feature_selection_support].columns,
                                                             target_names={1: "BBB+", 0: "BBB-"}))

    else:
        raise ValueError("Invalid group. Please choose 'cd' or 'cd_se_i'")


def get_lime_explainer_classification(classification_group):
    if classification_group == 'cd':
        X_train = X_train_cd
        y_train = y_train_cd
    elif classification_group == 'cd_se_i':
        X_train = X_train_cd_se_i.loc[:, feature_selection_support]
        y_train = y_train_cd_se_i
    else:
        raise ValueError("Invalid group. Please choose 'cd' or 'cd_se_i'")

    explainer = LimeTabularExplainer(training_data=np.array(X_train),
                                     mode='classification',
                                     feature_names=list(X_train.columns),
                                     training_labels=y_train,
                                     class_names=['BBB-', 'BBB+'],
                                     random_state=42)
    return explainer


def render_dataframe_as_table(dataframe):
    dataframe = dataframe.round(5)
    st.table(dataframe)


def user_inputs_section(category="cd"):
    mw = st.number_input("Molecular Weight (MW)", min_value=0.0, key=category,
                         help="Molecular weight or molecular mass refers to the mass of a molecule. It is calculated as the sum of the mass of each constituent atom multiplied by the number of atoms of that element in the molecular formula.")
    tpsa = st.number_input("Topological Polar Surface Area (TPSA)", min_value=0.0, key=category,
                           help="The topological polar surface area (TPSA) of a molecule is defined as the surface sum over all polar atoms in a molecule.")
    xlogp = st.number_input("XLogP3-AA (XLogP)", min_value=0.0, key=category,
                            help="Computed Octanol/Water Partition Coefficient")
    nhd = st.number_input("Hydrogen Bond Donor Count (NHD)", min_value=0.0, key=category,
                          help="The number of hydrogen bond donors in the structure.")
    nha = st.number_input("Hydrogen Bond Acceptor Count (NHA)", min_value=0.0, key=category,
                          help="The number of hydrogen bond acceptors in the structure.")
    nrb = st.number_input("Rotatable Bond Count (NRB)", min_value=0.0, key=category,
                          help="A rotatable bond is defined as any single-order non-ring bond, where atoms on either side of the bond are in turn bound to nonterminal heavy (i.e., non-hydrogen) atoms. That is, where rotation around the bond axis changes the overall shape of the molecule, and generates conformers which can be distinguished by standard fast spectroscopic methods.")
    side_effects_chosen = None
    indications_chosen = None

    if category == "cd_se_i":
        side_effects_chosen = st.multiselect("Side Effects", side_effects, key=category)
        indications_chosen = st.multiselect("Indications", indications, key=category)

    return mw, tpsa, xlogp, nhd, nha, nrb, side_effects_chosen, indications_chosen


def result_column_section(model, model_name, user_inputs, classification_group):
    st.markdown("##### Result")
    if model_name not in ["Support Vector Classification", "Stochastic Gradient Descent Classifier"]:
        prediction_probability = model.predict_proba(user_inputs)
        st.markdown(
            f"Probability that it cannot enter the brain: **{prediction_probability[0][0]:.5f}**")
        st.markdown(f"Probability that it can enter the brain: **{prediction_probability[0][1]:.5f}**")

    prediction = model.predict(user_inputs)
    if prediction == 1:
        st.markdown("""
                    The model has predicted that the compound/drug with the specific chemical properties you have specified **Can cross the BBB**
                    """)
    else:
        st.markdown("""
                    The model has predicted that the compound/drug with the specific chemical properties you have specified **Cannot cross the BBB**
                    """)

    if model_name not in ["Support Vector Classification", "Stochastic Gradient Descent Classifier"]:
        explainer = get_lime_explainer_classification(classification_group)
        if classification_group == 'cd':
            exp = explainer.explain_instance(user_inputs.squeeze(), model.predict_proba, num_features=6)
        else:
            exp = explainer.explain_instance(user_inputs.squeeze(), model.predict_proba, num_features=20)

        st.markdown("##### Prediction Explanation")
        st.pyplot(exp.as_pyplot_figure())

    if model_name not in ["Dummy Classifier", "Support Vector Classification", "K-Nearest Neighbour Classifier"]:
        st.markdown("##### Model Weights")
        st.write(model_weights_classification(model, classification_group))


def app():
    useful_info = st.container()
    cd_models = st.container()
    cd_chosen_model_and_inputs, cd_prediction_metrics = st.columns(2)
    cd_se_i_models = st.container()
    cd_se_i_important_side_effects, cd_se_i_important_indications = st.columns(2)
    cd_se_i_chosen_model_and_inputs, cd_se_i_prediction_metrics = st.columns(2)

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
        training_performance_cd = pd.read_csv(
            "Streamlit_App/data/Metrics/Classification_Models_CD_Training_Metrics.csv",
            skiprows=1)
        render_dataframe_as_table(training_performance_cd)

        st.markdown("##### Testing Performance")
        testing_performance_cd = pd.read_csv(
            "Streamlit_App/data/Metrics/Classification_Models_CD_Testing_Metrics.csv", skiprows=1)
        render_dataframe_as_table(testing_performance_cd)

        with cd_chosen_model_and_inputs:
            st.markdown("##### Make Predictions")
            st.markdown("""
                        - Please choose a model and enter a decimal number for each of the 6 chemical descriptors
                        - Helpful definitions are available for each descriptor. To access them click the question mark icon
                        """)

            cd_chosen_model = st.selectbox('Please choose a model to make predictions',
                                           cd_model_name_to_file.keys(),
                                           key="cd")
            if cd_chosen_model != "-":
                mw, tpsa, xlogp, nhd, nha, nrb, side_effects_chosen, indications_chosen = user_inputs_section()

                if st.button("Predict", key="cd"):
                    with cd_prediction_metrics:
                        model = load(
                            f"Streamlit_App/data/Classification_Models/CD/{cd_model_name_to_file[cd_chosen_model]}")
                        user_inputs = pd.DataFrame([[mw, tpsa, xlogp, nhd, nha, nrb]],
                                                   columns=['MW', 'TPSA', 'XLogP', 'NHD', 'NHA', 'NRB'])

                        result_column_section(model, cd_chosen_model, user_inputs, 'cd')

    with cd_se_i_models:
        st.subheader("Category 2: Models with Chemical Descriptors, Side Effects and Indications used as features")

        st.markdown("##### Feature Selection")
        st.markdown("""
                    - Feature selection was used in order to find the most chemical descriptors, side effects and indications and to improve the models' training times
                    - [Recursive Feature Elimination with Cross Validation (RFECV)](https://scikit-learn.org/stable/modules/generated/sklearn.feature_selection.RFECV.html) was used with a 10-Fold Cross Validation and a Random Forest Classifier optimised for F1 score
                       - Features were reduced from 4353 to 217
                       - All 6 chemical descriptors were kept
                       - 196 of the side effects were kept
                       - 15 of indications were kept 
                    """)
        with cd_se_i_important_side_effects:
            st.markdown("##### Important Side Effects")
            st.dataframe(side_effects)

        with cd_se_i_important_indications:
            st.markdown("##### Important Indications")
            st.dataframe(indications)

        st.markdown("##### Training Performance With Feature Selection")
        training_performance_cd_se_i = pd.read_csv(
            "Streamlit_App/data/Metrics/Classification_Models_CD_SE_I_Training_Metrics.csv",
            skiprows=1)
        render_dataframe_as_table(training_performance_cd_se_i)

        st.markdown("##### Testing Performance With Feature Selection")
        testing_performance_cd_se_i = pd.read_csv(
            "Streamlit_App/data/Metrics/Classification_Models_CD_SE_I_Testing_Metrics.csv",
            skiprows=1)
        render_dataframe_as_table(testing_performance_cd_se_i)

        with cd_se_i_chosen_model_and_inputs:
            st.markdown("##### Make Predictions")
            st.markdown("""
                        - Please choose a model, enter a decimal number for each of the 6 chemical descriptors and then pick one or multiple side effects and indications
                        - Helpful definitions are available for each descriptor. To access them click the question mark icon
                        """)

            cd_se_i_chosen_model = st.selectbox('Please choose a model to make predictions',
                                                cd_se_i_model_name_to_file.keys(),
                                                key="cd_se_i")
            if cd_se_i_chosen_model != "-":
                mw, tpsa, xlogp, nhd, nha, nrb, side_effects_chosen, indications_chosen = user_inputs_section("cd_se_i")

                if st.button("Predict", key="cd_se_i"):
                    with cd_se_i_prediction_metrics:
                        model = load(
                            f"Streamlit_App/data/Classification_Models/CD_SE_I/{cd_se_i_model_name_to_file[cd_se_i_chosen_model]}")

                        user_inputs = pd.DataFrame(columns=feature_selection_dataframe[0])
                        user_inputs.loc[0, "MW"] = mw
                        user_inputs.loc[0, "TPSA"] = tpsa
                        user_inputs.loc[0, "XLogP"] = xlogp
                        user_inputs.loc[0, "NHD"] = nhd
                        user_inputs.loc[0, "NHA"] = nha
                        user_inputs.loc[0, "NRB"] = nrb
                        for side_effect in side_effects_chosen:
                            user_inputs.loc[0, f"Side_Effect_{side_effect}"] = 1
                        for indication in indications_chosen:
                            user_inputs.loc[0, f"Indication_{indication}"] = 1
                        user_inputs.fillna(0, inplace=True)

                        result_column_section(model, cd_se_i_chosen_model, user_inputs, 'cd_se_i')
