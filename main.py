import requests
import sys

ok = requests.get(url = "https://app-authenticator-6690c-default-rtdb.firebaseio.com/.json")
if ok.status_code == 200:
    if ok.json().get("PLANEJAMENTO","").get("downloadVolumetry","") == False:
        sys.exit()
    else:
        from assets.startJms import *
else:
    sys.exit()