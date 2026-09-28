import io
import json
from datetime import datetime
import pdfplumber
import requests

URL_PDF = "https://dimec.unipg.it/files/docs/sezioni/sezione-cdlm-medicina-e-chirurgia/documenti/orario-lez-peru/4-anno_canale-a.pdf"


def fetch_and_parse_pdf():
  # Simula la richiesta da un browser standard per evitare blocchi HTTP 403
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
          " (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
      )
  }

  print(f"Scaricamento del PDF da: {URL_PDF}")
  response = requests.get(URL_PDF, headers=headers, timeout=30)
  print(f"Risposta del server HTTP: {response.status_code}")
  response.raise_for_status()

  events = []
  with pdfplumber.open(io.BytesIO(response.content)) as pdf:
    print(f"Pagine trovate nel PDF: {len(pdf.pages)}")
    for page_num, page in enumerate(pdf.pages, start=1):
      tables = page.extract_tables()
      for table in tables:
        if not table:
          continue
        for row in table:
          clean_row = [
              str(cell).replace("\n", " ").strip() if cell else ""
              for cell in row
          ]
          if any(clean_row):
            events.append({"pagina": page_num, "dati_riga": clean_row})

  payload = {
      "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
      "total_events": len(events),
      "events": events,
  }

  with open("schedule.json", "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)

  print(
      f"File schedule.json creato con successo! Righe estratte: {len(events)}"
  )


if __name__ == "__main__":
  fetch_and_parse_pdf()
