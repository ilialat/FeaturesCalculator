import pandas as pd
import requests
import json

API_URL = "http://localhost:8000/features"

df = pd.read_csv('data/data.csv')


def parse_contracts(contracts):
    if pd.isna(contracts):
        return None
    return json.loads(contracts)


df['contracts'] = df['contracts'].apply(parse_contracts)


def get_features(row):

    payload = {
        "id": str(row["id"]),
        "application_date": row["application_date"],
        "contracts": json.dumps(row["contracts"])
    }
    response = requests.post(API_URL, json=payload)

    features = response.json()
    return pd.Series(features)


# Apply the function to each row in the dataframe
features_df = df.apply(get_features, axis=1)
df = pd.concat([df, features_df], axis=1)


df.to_csv('data/contract_features.csv', index=False)
