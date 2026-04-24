import pdfplumber
import re

def extract(text, keywords):
    for k in keywords:
        m = re.search(rf"{k}.*?([\d,]+)", text, re.DOTALL)
        if m:
            return float(m.group(1).replace(",", ""))
    return 0


def parse_financials(file):

    text = ""

    with pdfplumber.open(file) as pdf:
        for p in pdf.pages:
            text += p.extract_text() or ""

    return {
        "bs": {
            "cash": extract(text, ["現金"]),
            "ar": extract(text, ["應收帳款"]),
            "inventory": extract(text, ["存貨"]),
            "assets": extract(text, ["資產總計"]),
            "liabilities": extract(text, ["負債總計"]),
            "equity": extract(text, ["權益總計"]),
        },
        "is": {
            "revenue": extract(text, ["營業收入"]),
            "gross_profit": extract(text, ["營業毛利"]),
            "net_income": extract(text, ["本期淨利"]),
        },
        "cf": {
            "ocf": extract(text, ["營業活動現金流量"])
        }
    }
