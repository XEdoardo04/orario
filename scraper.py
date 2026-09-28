import io
import json
from datetime import datetime
import pdfplumber
import requests

# URL diretto al PDF dell'orario
URL_PDF = "https://dimec.unipg.it/files/docs/sezioni/sezione-cdlm-medicina-e-chirurgia/documenti/orario-lez-peru/4-anno_canale-a.pdf"


def fetch_and_parse_pdf():
  print("Download del PDF in corso...")
  response = requests.get(URL_PDF)
  response.raise_for_status()

  events = []

  # Apre il PDF direttamente dallo stream in memoria
  with pdfplumber.open(io.BytesIO(response.content)) as pdf:
    for page_num, page in enumerate(pdf.pages, start=1):
      # Estrae le tabelle presenti nella pagina corrente
      tables = page.extract_tables()

      for table in tables:
        if not table:
          continue

        for row in table:
          # Pulisce il testo di ciascuna cella da spazi vuoti e a capo superflui
          clean_row = [
              str(cell).replace("\n", " ").strip() if cell else ""
              for cell in row
          ]

          # Ignora le righe completamente vuote
          if not any(clean_row):
            continue

          # Inserisce i dati grezzi estratti dalla tabella
          events.append({"pagina": page_num, "dati_riga": clean_row})

  payload = {
      "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
      "total_events": len(events),
      "events": events,
  }

  # Salva il risultato in JSON
  with open("schedule.json", "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)

  print(
      f"Completato! Salvati {len(events)} elementi estratti in schedule.json"
  )


if __name__ == "__main__":
  fetch_and_parse_pdf()