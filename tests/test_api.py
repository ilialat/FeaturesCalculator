import json
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_no_claims():

    payload = {
        "id": "1",
        "application_date": "2025-03-15 00:00:00.000000+00:00",
        "contracts": ""
    }
    print(f"Payload: {payload}")
    response = client.post("/features", json=payload)
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.content}")
    assert response.status_code == 200
    data = response.json()

    assert data["tot_claim_cnt_l180d"] == -3
    assert data["disb_bank_loan_wo_tbc"] == -3
    assert data["day_sinlastloan"] == -3

def test_claims_exist():

    payload = {
        "id": "2",
        "application_date": "2025-03-15 00:00:00.000000+00:00",
        "contracts": json.dumps([
            {
                "claim_id": "22",
                "claim_date": "01.03.2025",
                "bank": "ZIRAAT",
                "loan_summa": "1500",
                "contract_date": "",  # not disbursed due to missing contract_date
                "summa": "1500",
            },
            {
                "claim_id": "23",
                "claim_date": "11.03.2025",
                "bank": "HALYK",
                "loan_summa": "500",
                "contract_date": "13.03.2025",  # disbursed 2 days
                "summa": "500",
            }
        ])
    }
    response = client.post("/features", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["tot_claim_cnt_l180d"] == 2
    assert data["disb_bank_loan_wo_tbc"] == 500
    assert data["day_sinlastloan"] == 2
