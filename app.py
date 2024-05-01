from fastapi import HTTPException, status, Security, FastAPI, Form
from bs4 import BeautifulSoup
from fastapi.security import APIKeyHeader, APIKeyQuery
from typing import Union
from tui_module import TUI
from tnrib_module import TNRIB
import requests
import json
import httpx

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

@app.post("/whois/")
async def whois(domain: str = Form(...)):
    url = "https://whois.ati.tn/"

    payload = f"domain={domain}&ext=1&submit=ok&b_existe=Existe%3F"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'https://registre.tn/',
        'User-Agent': 'insomnia/2023.5.8'
    }

    cookies = {
        'PHPSESSID': '1oi1k48jki92f6r5lg36cdprv2'
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=payload, cookies=cookies)
        page = BeautifulSoup(response.text, 'html.parser')

        # Selecting the specific div
        t = page.select_one('#middle > div')

        # Creating a new BeautifulSoup object from the selected div
        soup = BeautifulSoup(str(t), 'html.parser')

        whois_result = {}

        domain_status_tag = soup.find('strong', style='color:#C00;')

        if domain_status_tag:
            domain_status = domain_status_tag.text
        else:
            domain_status_tag = soup.find('span', style='color:#C00;')
            if domain_status_tag:
                domain_status = domain_status_tag.text
            else:
                domain_status = "not registered domain"
                return {"WhoisResult": domain_status}

        # Extracting domain name and status
        domain_name_tag = soup.find('a')
        if domain_name_tag:
            domain_name = domain_name_tag.text
        else:
            whois_result['DomainStatus'] = "Le domaine est libre pour l'instant."
            whois_result['DomainName'] = domain_status
            return {"WhoisResult": whois_result}

        whois_result['DomainName'] = domain_name
        whois_result['DomainStatus'] = domain_status

        # Extracting creation date and domain state
        details = soup.find_all('ul')
        creation_date = details[0].li.text.replace('Date création: ', '')
        domain_state = details[1].li.text.replace('Etat domaine: ', '')
        whois_result['CreationDate'] = creation_date
        whois_result['DomainState'] = domain_state

        # Extracting registrar
        registrar = details[2].li.a.text
        whois_result['Registrar'] = registrar

        # Extracting registrant details
        registrant_info = details[3:11]
        registrant = {}
        for info in registrant_info:
            key = info.li.strong.text.replace(':', '').strip()
            value = info.li.text.split(':')[-1].strip()
            registrant[key] = value
        whois_result['Registrant'] = registrant

        # Extracting administrative contact details
        admin_contact_info = details[11:19]
        admin_contact = {}
        for info in admin_contact_info:
            key = info.li.strong.text.replace(':', '').strip()
            value = info.li.text.split(':')[-1].strip()
            admin_contact[key] = value
        whois_result['AdministrativeContact'] = admin_contact

        # Extracting technical contact details
        tech_contact_info = details[19:27]
        tech_contact = {}
        for info in tech_contact_info:
            key = info.li.strong.text.replace(':', '').strip()
            value = info.li.text.split(':')[-1].strip()
            tech_contact[key] = value
        whois_result['TechnicalContact'] = tech_contact

        # Extracting DNS servers
        dns_servers = [item.li.text.replace('Nom : ', '') for item in details[-3:-1]]
        whois_result['DNSServers'] = dns_servers

        return {"WhoisResult": whois_result}
        
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
