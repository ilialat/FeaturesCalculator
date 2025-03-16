# FeaturesCalculator

This assignment is designed to help you practice your data parsing and feature engineering skills
while building a web service using FastAPI. You will be given a dataset called data.csv that contains
three columns: id, application_date, and contracts. The contracts column is a JSON string that
contains information about the contracts that a customer has signed up for. Your task is to parse
this JSON and calculate a set of features from it.

## Description
* Output File - data/contract_features.csv
* Code that generated output file - helper/scorer.py
* Feature Calculator - src/feature_calculator.py
* FastAPI - src/main.py

## Run App

```sh  
docker build -t features-calculator .
```

```sh  
 docker run -p 8000:8000 features-calculator
```