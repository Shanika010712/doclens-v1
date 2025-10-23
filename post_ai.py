# utils/ai_post.py
import json, re

def normalise_ai_string(raw: str):
    """
    Turns raw bracket-delimited strings like
    [BANK|NAME|NIC|DATE|TIN|CERT],[ACC|CUR],...
    into a structured dict that the front-end already knows.
    """
    if not raw or raw[0] != "[":
        return None           # already JSON or unexpected
    chunks = re.findall(r'\[([^\]]+)\]', raw)
    if not chunks:
        return None

    # first chunk = general info (6 parts)
    gi_items = chunks[0].split("|")
    general_info = {
        "bank": gi_items[0],
        "customer_name": gi_items[1],
        "nic": gi_items[2],
        "issued_date": gi_items[3],
        "tin": gi_items[4],
        "wht_cert_no": gi_items[5],
    }

    # every next = account + periods
    accounts = []
    i = 1
    while i < len(chunks):
        acc_no, currency = chunks[i].split("|")
        i += 1
        periods = []
        while i < len(chunks) and chunks[i].count("|") == 2:
            month, interest, wht = chunks[i].split("|")
            periods.append(
                {"period_name": month,
                 "interest": interest,
                 "wht": wht}
            )
            i += 1
        accounts.append({"account_no": acc_no,
                         "currency": currency,
                         "periods": periods})
    return {"general_info": general_info, "accounts": accounts}
