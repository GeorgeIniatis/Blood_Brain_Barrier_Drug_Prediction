# Readme

- `Classification_Models/` and `Regression_Models/` directories contain all our trained classification and regression models, respectively, in the form of .joblib files
- `Dataset_Files/` contain all the different datasets used in our project. From our own dataset to the SIDER side effects and indications
- `Feature_Selection/` contains the top features discovered after running RFECV in the form of a numpy array
- `Metrics/` contains all the metrics recorded from training and testing our models
- `Streamlit_App/` contains anything to do with our web app
- `modify_dataset.py` contains multiple functions that were created to help us create our dataset
- `pubmed_api_calls.py` and `pubmed_api_calls.py` contain multiple functions and regular expressions that were created to help us query the PubMed and SPRINGER APIs, respectively
- `notebook.ipynb` is the Jupyter Notebook used that was used to train and test our models

## Build instructions

No particular build instructions needed. Anyone with Python can access the different function used in `modify_dataset.py`, `pubmed_api_calls.py` and `pubmed_api_calls.py`, and as for `notebook.ipynb` you just need a Jupyter installation.

### Requirements

* Python 3.10
* Packages: listed in `requirements.txt` 
* Tested on Windows 11

### Build steps

`pip install -r requirements.txt`

### Test steps

Since this is an ML project with most of the work done on the notebook we would advise just opening `notebook.ipynb` using your preferred method of opening Jupyter notebooks and running it.
We should also mention that an online version of the notebook is hosted on Datalore, which you can access using this link: [Datelore Notebook](https://datalore.jetbrains.com/notebook/IczIzzNdfezZefWuhmeMRx/D9Y5hyorcCW5ScYTdMTeab/)





