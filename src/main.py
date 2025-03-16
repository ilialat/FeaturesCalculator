from fastapi import FastAPI
from src.feature_calculator import ContractFeatureCalculator
from src.models import ApplicationData, FeatureResponse
import uvicorn
from fastapi import HTTPException

app = FastAPI(title="Feature Engineering")
feature_calculator = ContractFeatureCalculator()


@app.post("/features", response_model=FeatureResponse, summary="Compute application features")
def compute_features(application_data: ApplicationData):
    try:
        data = application_data.dict()
        features = feature_calculator.calculate(data)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"ValueError: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Exception: {str(e)}")
    return features


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
