import requests
import datetime


def update_appefficiency_info(apptag, final_time, quantity:int = 1):

    ano =(datetime.datetime.today()).strftime("%Y")
    mes = (datetime.datetime.today()).strftime("%m")
    dia = (datetime.datetime.today()).strftime("%d")

    url = f"https://appefficiency-3f979-default-rtdb.firebaseio.com/{apptag}/records/{ano}/{mes}/{dia}-{mes}-{ano}.json"

    result = requests.get(url = url)

    if result.json() is not None:

        payload = {
            "elapsed-time": result.json()["elapsed-time"] + final_time,
            "quantity": result.json()["quantity"] + quantity
        }

    else:
        payload = {
            "quantity": quantity,
            "elapsed-time": final_time
        }

    requests.put(url = url, json = payload)


# import time
# start = time.perf_counter() # marca o inicio da execução do script
# final_time = round((time.perf_counter() - start) / 60, 2)
# update_appefficiency_info("TESTE", final_time = final_time)