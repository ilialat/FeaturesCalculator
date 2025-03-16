from pydantic import BaseModel


class ApplicationData(BaseModel):
    id: str
    application_date: str
    contracts: str


class FeatureResponse(BaseModel):
    tot_claim_cnt_l180d: int
    disb_bank_loan_wo_tbc: int 
    day_sinlastloan: int
