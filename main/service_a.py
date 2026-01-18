from fastapi import FastAPI
from pydantic import BaseModel
import datetime

app = FastAPI()

class AnalysisResult(BaseModel):
    url: str
    person_count: int
    processing_time: float

results_db = []

@app.post("/results")
def save_result(result: AnalysisResult):
    print(f" [Serwis A] Otrzymano wynik: {result.person_count} osób na zdjęciu.")
    results_db.append({
        "data": result,
        "timestamp": datetime.datetime.now()
    })
    return {"status": "saved"}

@app.get("/results")
def get_results():
    return results_db