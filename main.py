import requests
import sys
import schedule
import time
from assets.startJms import ProjetoJMS


def main():
    ok = requests.get(url = "https://app-authenticator-6690c-default-rtdb.firebaseio.com/.json")
    if ok.status_code == 200:
        if ok.json().get("PLANEJAMENTO","").get("downloadVolumetry","") == False:
            sys.exit()
        else:
            ProjetoJMS().start()
    else:
        sys.exit()


schedule.every().day.at('02:30').do(main)
schedule.every().day.at('07:00').do(main)
schedule.every().day.at('12:30').do(main)
schedule.every().day.at('16:30').do(main)
schedule.every().day.at('18:30').do(main)
schedule.every().day.at('21:30').do(main)

while True:
    schedule.run_pending()
    time.sleep(30)

