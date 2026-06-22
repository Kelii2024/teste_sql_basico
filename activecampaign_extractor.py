import os
import requests
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

AC_API_URL = os.getenv("AC_API_URL", "https://bling25662.api-us1.com")
AC_API_KEY = os.getenv("AC_API_KEY")
SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")

HEADERS = {"Api-Token": AC_API_KEY}

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def fetch_all(endpoint: str, key: str) -> list:
    """Pagina automaticamente todos os registros de um endpoint."""
    results = []
    offset = 0
    limit = 100
    while True:
        url = f"{AC_API_URL}/api/3/{endpoint}?limit={limit}&offset={offset}"
        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()
        batch = data.get(key, [])
        results.extend(batch)
        total = int(data.get("meta", {}).get("total", len(results)))
        offset += limit
        if offset >= total:
            break
    return results


def extract_campaigns() -> pd.DataFrame:
    campaigns = fetch_all("campaigns", "campaigns")
    rows = []
    for c in campaigns:
        rows.append({
            "id": c.get("id"),
            "nome": c.get("name"),
            "tipo": c.get("type"),
            "status": c.get("status"),
            "assunto": c.get("subject"),
            "remetente_nome": c.get("fromname"),
            "remetente_email": c.get("fromemail"),
            "total_enviados": c.get("send_amt", 0),
            "total_abertos": c.get("opens", 0),
            "total_cliques": c.get("uniquelinkclicks", 0),
            "total_descadastros": c.get("unsubscribes", 0),
            "total_bounces": c.get("hardbounces", 0),
            "taxa_abertura": c.get("opens_rate", 0),
            "taxa_clique": c.get("clicks_rate", 0),
            "data_envio": c.get("sdate"),
            "data_criacao": c.get("cdate"),
            "atualizado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })
    return pd.DataFrame(rows)


def extract_automations() -> pd.DataFrame:
    automations = fetch_all("automations", "automations")
    rows = []
    for a in automations:
        rows.append({
            "id": a.get("id"),
            "nome": a.get("name"),
            "status": a.get("status"),
            "ativa": a.get("hidden") == "0",
            "total_contatos": a.get("contactGoalCount", 0),
            "contatos_ativos": a.get("activeContacts", 0),
            "contatos_concluidos": a.get("completeCount", 0),
            "data_criacao": a.get("cdate"),
            "data_modificacao": a.get("mdate"),
            "atualizado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })
    return pd.DataFrame(rows)


def get_sheet_client():
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    return gspread.authorize(creds)


def upload_to_sheets(df: pd.DataFrame, sheet_name: str):
    client = get_sheet_client()
    spreadsheet = client.open_by_key(SHEET_ID)

    try:
        worksheet = spreadsheet.worksheet(sheet_name)
        worksheet.clear()
    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=5000, cols=30)

    df = df.fillna("").astype(str)
    worksheet.update([df.columns.tolist()] + df.values.tolist())
    print(f"  [{sheet_name}] {len(df)} registros enviados para o Google Sheets.")


def main():
    if not AC_API_KEY:
        raise ValueError("AC_API_KEY não definida. Configure o arquivo .env")
    if not SHEET_ID:
        raise ValueError("GOOGLE_SHEET_ID não definido. Configure o arquivo .env")

    print("Extraindo campanhas...")
    df_campaigns = extract_campaigns()
    upload_to_sheets(df_campaigns, "Campanhas")

    print("Extraindo automações...")
    df_automations = extract_automations()
    upload_to_sheets(df_automations, "Automacoes")

    print("\nConcluido! Dados enviados para o Google Sheets.")
    print(f"  Campanhas: {len(df_campaigns)} registros")
    print(f"  Automacoes: {len(df_automations)} registros")


if __name__ == "__main__":
    main()
