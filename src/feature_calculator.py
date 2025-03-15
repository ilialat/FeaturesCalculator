import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


class ContractFeatureCalculator():
    def parse_contracts(self, contracts_json: str) -> List[Dict[str, Any]]:
        """
        Converts the contracts JSON string into a list of dictionaries.
        """
        data = json.loads(contracts_json)
        if not isinstance(data, list):
            raise ValueError("contracts JSON is not a list.")

        return data

    def calculate_tot_claim_cnt_l180d(
        self, contracts: List[Dict[str, Any]], application_date: datetime
    ) -> int:
        """
        Calculate the number of claims made in the 180 days before the "application_date".

        A claim is considered valid if:
          1) 'claim_id' is not null.
          2) 'claim_date' is not null and falls within [application_date - 180 days, application_date].

        Returns:
            int: The count of valid claims. If no claim is present at all, returns -3.
        """
        found_claim = any(contract.get("claim_id") != "" for contract in contracts)
        
        if not found_claim:
            return -3        
        
        claim_cnt = 0
        min_date = application_date - timedelta(days=180)

        for contract in contracts:
            if contract.get("claim_id"):
                claim_date = contract.get("claim_date")
                if claim_date:
                    claim_date = datetime.strptime(claim_date, "%d.%m.%Y")
                    if min_date <= claim_date <= application_date:
                        claim_cnt += 1

        return claim_cnt

    def calculate_disb_bank_loan_wo_tbc(
        self, contracts: List[Dict[str, Any]]
    ) -> int:
        """
        Calculate sum of disbursed loans exposure without TBC loans.

        Special Notes:
          - Exclude loans where 'bank' is in ['LIZ', 'LOM', 'MKO', 'SUG', None].
          - Exlude loans with a null 'contract_date'.

        Returns:
            int: Sum of loan_summa for valid loans.
                   If no claim records exist, returns -3.
                   If claims exist but no valid loan is found, returns -1.
        """

        total_loan_exposure = 0
        valid_loan_found = False

        for contract in contracts:
            bank = contract.get("bank")
            contract_date = contract.get("contract_date")
            loan_summa = contract.get("loan_summa")
            claim_id = contract.get("claim_id")

            # Skip if claim_id is missing.
            if claim_id == "":
                continue

            # Skip if bank is not allowed.
            if bank in ["LIZ", "LOM", "MKO", "SUG", None, ""]:
                continue
            
            # Skip if contract_date is missing.
            if not contract_date:
                continue

            if loan_summa != "":
                total_loan_exposure += int(loan_summa)  # Can it be a float also?   
                valid_loan_found = True

        return total_loan_exposure if valid_loan_found else -1

    def calculate_day_sinlastloan(
        self, contracts: List[Dict[str, Any]], application_date: datetime
    ) -> int:
        """
        Calculate the number of days since last loan.

        Special Notes:
          - Considers any loan record where both 'loan_summa' and 'contract_date' are not null.

        Returns:
            int: The days difference between 'application_date' and the most recent loan's 'contract_date'.
                 If no claim records exist, returns -3.
                 If claims exist but no valid loan is found, returns -1.
        """
        found_claim = any(contract.get("claim_id")
                          is not None for contract in contracts)

        if not found_claim:
            return -3

        most_recent_loan_date = None

        for contract in contracts:
            loan_summa = contract.get("loan_summa")
            contract_date_str = contract.get("contract_date")

            if not loan_summa or not contract_date_str:
                continue

            current_loan_date = datetime.strptime(
                contract_date_str, "%d.%m.%Y")

            if most_recent_loan_date is None or current_loan_date > most_recent_loan_date:
                most_recent_loan_date = current_loan_date

        if most_recent_loan_date is None:
            return -1

        return (application_date - most_recent_loan_date).days

    def calculate(self, data: dict) -> dict:
        """
        Wrapper - compute all three features.

        Expects data dictionary with keys:
            - id (str): Unique identifier for the record.
            - application_date (str): in YYYY-MM-DD format.
            - contracts (str): JSON string representing the list of contracts.

        Returns:
            dict: Dictionary with 3 keys:
                - tot_claim_cnt_l180d
                - disb_bank_loan_wo_tbc
                - day_sinlastloan

        Raises:
            ValueError: If required fields are missing.
        """
        # Check Identifiers
        application_date_str = data.get("application_date")
        application_id = data.get("id")

        if not application_date_str or not application_id:
            raise ValueError("application_date and id fields are required.")

        application_date = datetime.strptime(application_date_str, "%Y-%m-%d")

        # Check contracts
        contracts_json = data.get("contracts")
        if not contracts_json:
            raise ValueError("contracts field is required.")
        contracts = self.parse_contracts(contracts_json)
        
        logger.info(f"Calculating features for application {application_id}.")
        # Calculate number of claims made in the 180 days before the application_date.
        tot_claim_cnt = self.calculate_tot_claim_cnt_l180d(
            contracts, application_date)

        # Calculate the sum of disbursed loans exposure without TBC loans.
        disb_bank_loan = self.calculate_disb_bank_loan_wo_tbc(contracts)

        # Calculate days since the last loan.
        day_sinlastloan = self.calculate_day_sinlastloan(
            contracts, application_date)

        logger.info(f"Features calculated for application {application_id}.")
        
        return {
            "tot_claim_cnt_l180d": tot_claim_cnt,
            "disb_bank_loan_wo_tbc": disb_bank_loan,
            "day_sinlastloan": day_sinlastloan
        }
