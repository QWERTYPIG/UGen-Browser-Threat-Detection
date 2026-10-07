from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from src.inference.engine import InferenceEngine

app = FastAPI(title="BrowserOS Security Middleware")
inference_engine = InferenceEngine()

class PageState(BaseModel):
    url: str
    html_content: str
    screenshot_base64: Optional[str] = None

class ValidationResponse(BaseModel):
    is_safe: bool
    threat_type: Optional[str] = None
    reason: Optional[str] = None

@app.post("/validate", response_model=ValidationResponse)
async def validate_state(state: PageState):
    # Pass the state to the inference engine
    result = inference_engine.analyze(state.url, state.html_content, state.screenshot_base64)
    
    if not result["is_safe"]:
        # Log the threat or sanitize the context
        print(f"Threat detected on {state.url}: {result['threat_type']}")
        return ValidationResponse(
            is_safe=False,
            threat_type=result["threat_type"],
            reason=result["reason"]
        )
    
    return ValidationResponse(is_safe=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
