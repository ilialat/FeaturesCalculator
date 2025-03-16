import pytest
from datetime import datetime
from src.feature_calculator import ContractFeatureCalculator


@pytest.fixture
def feature_calculator():
    return ContractFeatureCalculator()


def test_tot_claim_cnt_l180d(feature_calculator):

    ex_1 = {
        "application_date": datetime.strptime("2025-03-15", "%Y-%m-%d"),
        "contracts": [
            {"claim_id": "21", "claim_date": "01.02.2025"},  # valid claim
            {"claim_id": "22", "claim_date": "01.09.2024"},  # invalid claim - outside 180 days window
            {"claim_id": "23", "claim_date": ""},          # invalid claim - no claim_date
            {"claim_id": "24", "claim_date": "01.03.2025"},  # valid claim
        ]
    }
    
    tot_claim_cnt_l180d = feature_calculator.calculate_tot_claim_cnt_l180d(
        ex_1["contracts"], ex_1["application_date"])

    assert tot_claim_cnt_l180d == 2


def test_disb_bank_loan_wo_tbc(feature_calculator):

    ex_1 = {
        "application_date": datetime.strptime("2025-03-15", "%Y-%m-%d"),
        "contracts": [
            {
                "claim_id": "12",
                "bank": "Ziraat",
                "loan_summa": "1500",
                "contract_date": "2025-01-20",
            },
            {
                "claim_id": "21",
                "bank": "LIZ",  # this loan should be excluded
                "loan_summa": "100",
                "contract_date": "2025-01-22",
            },
            {
                "claim_id": "22",
                "bank": "Halyk",
                "loan_summa": "2000",
                "contract_date": "",  # not disbursed - should be excluded
            },
            {
                "claim_id": "23",
                "bank": "Pasha", 
                "loan_summa": "",  # not disbursed - should be excluded
                "contract_date": "2025-02-22",
            }
        ]
    }
    
    ex_2 = {
        "application_date": datetime.strptime("2025-03-15", "%Y-%m-%d"),
        "contracts": [
            {
                "claim_id": "12",
                "bank": None,  # this loan should be excluded
                "loan_summa": "1231",
                "contract_date": "2025-01-20",
            },
            {
                "claim_id": "21",
                "bank": "LOM",  # this loan should be excluded
                "loan_summa": "",
                "contract_date": "2025-01-22",
            }
        ]
    }

            
    disb_bank_loan_wo_tbc = feature_calculator.calculate_disb_bank_loan_wo_tbc(
        ex_1["contracts"])

    disb_bank_loan_wo_tbc_2 = feature_calculator.calculate_disb_bank_loan_wo_tbc(
        ex_2["contracts"])
    
    assert disb_bank_loan_wo_tbc == 1500
    assert disb_bank_loan_wo_tbc_2 == -1


def test_day_sinlastloan(feature_calculator):
    # Scenario: Multiple loans; test to get days since the most recent one.
    data = {
        "application_date": datetime.strptime("2025-03-15", "%Y-%m-%d"),
        "contracts": [
            {
                "claim_id": "12",
                "summa": "1000",
                "contract_date": "10.03.2025"  # most recent loan
            },
            {
                "claim_id": "21",
                "summa": "500",
                "contract_date": "10.02.2025"  # older loan
            },
            {
                "claim_id": "22",
                "summa": "",
                "contract_date": "12.02.2025"   # invalid loan - summa missing
            },
            {
                "claim_id": "23",
                "summa": "200",
                "contract_date": "",   # invalid loan - contract_date missing
            },
        ]
    }
    day_sinlastloan = feature_calculator.calculate_day_sinlastloan(
        data["contracts"], data["application_date"])

    assert day_sinlastloan == 5
