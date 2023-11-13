from fastapi import HTTPException, status, Security, FastAPI
from fastapi.security import APIKeyHeader, APIKeyQuery
from typing import Union
from tui_module import TUI
from tnrib_module import TNRIB


api_keys = [
    "my_api_key"
]

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

def get_api_key(
        api_key_header: str = Security(api_key_header),
) -> str:
    if api_key_header in api_keys:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}
    
@app.get("/tui")
def is_valid(api_key: str = Security(get_api_key), s: Union[str, None] = None):
    if s:
        t = TUI(s)
        return {"result": t.is_valid()}
    return {"result": "VAT is not provided"}
    
@app.get("/tnrib")
def is_valid(api_key: str = Security(get_api_key), s: Union[str, None] = None):
    if s:
        tnrib_instance = TNRIB(s)
        if tnrib_instance.is_valid():
            return {"result": [{"IBAN": tnrib_instance.iban_val, "BIC": tnrib_instance.bic_val, "Account Number": tnrib_instance.account_number, "Bank Name": tnrib_instance.bank_name}]}
        else:
            return {"result": "BBAN is not valid"}
    return {"result": "BBAN is not provided"}
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
