import time, requests, logging
from django.conf import settings

log = logging.getLogger(__name__)

def get_salesforce_token(request):
    """
    Return a valid access-token, refreshing if older than 14 min
    or if Salesforce has already invalidated it.
    """
    sess = request.session
    issued_at = int(sess.get("sf_issued_at", 0)) / 1000  # → seconds
    age = time.time() - issued_at

    # 1) if token older than 14 min refresh proactively
    if age > 14 * 60:
        _refresh(request)

    return sess.get("sf_access_token")


def _refresh(request):
    sess = request.session
    refresh_token = sess.get("sf_refresh_token")
    if not refresh_token:
        raise RuntimeError("No refresh_token in session – user must re-auth.")

    payload = {
        "grant_type": "refresh_token",
        "client_id": settings.SALESFORCE_CLIENT_ID,
        "client_secret": settings.SALESFORCE_CLIENT_SECRET,
        "refresh_token": refresh_token,
    }
    r = requests.post(
        "https://login.salesforce.com/services/oauth2/token",
        data=payload,
        timeout=10,
    )
    r.raise_for_status()
    data = r.json()

    sess["sf_access_token"] = data["access_token"]
    sess["sf_instance_url"] = data["instance_url"]
    sess["sf_issued_at"]    = int(time.time()) * 1000
    sess.save()
    log.info("Salesforce access-token refreshed")
def get_accounts(request):
    token = get_salesforce_token(request)
    url   = request.session["sf_instance_url"] + "/services/data/v60.0/sobjects/Account"
    resp  = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=10)

    # if someone else killed the session you’ll still get 401 – catch & retry once
    if resp.status_code == 401:
        get_salesforce_token(request)  # forces refresh
        token = request.session["sf_access_token"]
        resp  = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=10)

    resp.raise_for_status()
    return resp.json()