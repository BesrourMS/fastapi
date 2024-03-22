from fastapi import HTTPException, status, Security, FastAPI
from fastapi.security import APIKeyHeader, APIKeyQuery
from typing import Union
from tui_module import TUI
from tnrib_module import TNRIB
import requests


api_keys = [
    "WzIsImhhbWVkIEhhd2FyaSJd"
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
async def is_valid(api_key: str = Security(get_api_key), s: Union[str, None] = None):
    if s:
        t = TUI(s)
        if t.is_valid():
            try:
                response = requests.get('https://www.registre-entreprises.tn/rne-api/public/registres/pm?idUnique=' + s)
                response.raise_for_status()  # Raise exception for 4XX or 5XX status codes
                return {"result": response.json(), "status": response.status_code}
            except requests.exceptions.HTTPError as e:
                return {"result": "Company does not exist in the database."}
        else:
            return {"result": "VAT is not valid"}
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
    
@app.get("/rne")
async def is_valid(api_key: str = Security(get_api_key), s: Union[str, None] = None):
    if s:
        try:
            response = requests.get('https://www.registre-entreprises.tn/rne-api/public/registres/pm/' + s)
            response.raise_for_status()  # Raise exception for 4XX or 5XX status codes
            return {"result": response.json(), "status": response.status_code}
        except requests.exceptions.HTTPError as e:
            return {"result": "Company does not exist in the database."}
    return {"result": "RNE is not provided"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
