# import requests
# import datetime
# import os
# import pandas as pd

# class JMS_Report:
#     def __init__(self, authtoken):
#         self.authtoken = authtoken
#         self.start_date = (datetime.datetime.today() - datetime.timedelta(1)).strftime("%Y-%m-%d")
#         self.end_date = (datetime.datetime.today() + datetime.timedelta(1)).strftime("%Y-%m-%d")

#         self.transport_ids = []

#         self.final_wb = []

#     def sc_transport_id(self) -> list:
        
#         url = f"https://gw.jtjms-br.com/transportation/tmsShipment/page?current=1&size=20&startCode=31101&startDateTime={self.start_date}+15:00:00&endDateTime={self.end_date}+15:00:00&searchType=manage"
#         header = {"authToken": self.authtoken}

#         response = requests.get(url = url, headers = header)
#         if response.status_code == 200 and "data" in response.json() and "records" in response.json()["data"]:
#             records = response.json()["data"]["records"]
#         else:
#             print("Erro na resposta SC:", response.text)
#             return
        
#         for record in records:
#             if ("SJM" in record["shipmentName"] or "BSB" in record["shipmentName"] or "CGE" in record["shipmentName"]) and record["shipmentState"] in [2,3,4]:
#                 self.transport_ids.append([record["shipmentNo"], record["createTime"]])

#     def dc_transport_id(self) -> list:
#         url = "https://gw.jtjms-br.com/transportation/tmsBranchTrackingDetail/page"
#         header = {"authtoken": self.authtoken}
#         payloads = [{"current":1,"size":20,"startDepartureTime":"2024-12-09 00:00:00","endDepartureTime":"2024-12-09 23:59:59","endCode":"316001","countryId":"1"},
#                     {"current":1,"size":20,"startDepartureTime":"2024-12-09 00:00:00","endDepartureTime":"2024-12-09 23:59:59","endCode":"535105","countryId":"1"},
#                     {"current":1,"size":20,"startDepartureTime":"2024-12-09 06:00:00","endDepartureTime":"2024-12-10 06:00:00","endCode":"535104","countryId":"1"}]
        
#         for payload in payloads:

#             response = requests.post(url = url, headers = header, json = payload)
#             records = response.json()["data"]["records"]

#             for record in records:
#                 self.transport_ids.append([record["shipmentNo"], record["createTime"]])

#     def start(self):
#         self.sc_transport_id() # É necessário pesquisar por esses IDs de viagem através da Consulta de Viagem
#         self.dc_transport_id() # É necessário pesquisar por esses IDs de viagem através da Consulta de Bipagem

#         # # Coleta de peças Troncais
#         # for shipment_number, start_code in self.transport_ids:
#         #     header = {"authtoken": self.authtoken}

#         #     print(shipment_number)
#         #     total_url = f"https://gw.jtjms-br.com/transportation/trackingDeatil/loading/scan/list?shipmentNo={shipment_number}"
#         #     total_response = requests.get(url = total_url, headers = header)

#         #     total_response = total_response.json()["data"][0]["scanWaybillNum"]
#         #     url = f"https://gw.jtjms-br.com/transportation/trackingDeatil/loading/scan/page?current=1&size=999999&shipmentNo={shipment_number}&scanNetworkCode={start_code}&countNum={total_response}"
#         #     print(url)
#         #     response = requests.get(url = url, headers = header)
#         #     total = response.json()
#         #     print(total)

#         url = "https://gw.jtjms-br.com/operatingplatform/scanRecordQuery/listPage"
#         header = {"authtoken": self.authtoken}
#         payload = {
#             "current":1,
#             "size":100,
#             "startDates":"2024-12-07 00:00:00",
#             "endDates":"2024-12-09 23:59:59",
#             "scanSite":"31101",
#             "scanType":"装车扫描",
#             "transferCode":"DKGX24120900018",
#             "sortName":"scanDate",
#             "sortOrder":"asc",
#             "bilNos":[],
#             "querySub":"querySub",
#             "reachAddressList":[],
#             "sendSites":[],
#             "billType":1,
#             "countryId":"1"
#             }
#         for shipment_number, start_date in self.transport_ids:
#             total_page = requests.post(url = url, headers = header, json = payload).json()["data"]["pages"]
#             end_date = datetime.datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(days = 4)
#             for i in range(1, total_page):
#                 payload = {**payload, "startDates": start_date, "endDates": end_date,"transferCode": shipment_number, "current": i}
#                 print(payload)
#                 response = requests.post(url = url, headers = header, json = payload)


#     def fetch_data(self):
#         self.sc_transport_id() # É necessário pesquisar por esses IDs de viagem através da Consulta de Viagem
#         self.dc_transport_id() # É necessário pesquisar por esses IDs de viagem através da Consulta de Bipagem
#         url = "https://gw.jtjms-br.com/operatingplatform/scanRecordQuery/listPage"
#         header = {"authToken": self.authtoken}
        
#         base_payload = {
#             "current": 1,
#             "size": 100,
#             "startDates": "",
#             "endDates": "",
#             "scanSite": "31101",
#             "scanType": "装车扫描",
#             "transferCode": "",
#             "sortName": "scanDate",
#             "sortOrder": "asc",
#             "bilNos": [],
#             "querySub": "querySub",
#             "reachAddressList": [],
#             "sendSites": [],
#             "billType": 1,
#             "countryId": "1"
#         }

#         for shipment_number, start_date in self.transport_ids:
#             try:
#                 # Calcular data final
#                 start_date_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
#                 end_date_dt = start_date_dt + datetime.timedelta(days=4)
                
#                 # Atualizar o payload inicial para obter o total de páginas
#                 initial_payload = {
#                     **base_payload,
#                     "startDates": start_date_dt.strftime("%Y-%m-%d %H:%M:%S"),
#                     "endDates": end_date_dt.strftime("%Y-%m-%d %H:%M:%S"),
#                     "transferCode": shipment_number
#                 }
#                 response = requests.post(url=url, headers=header, json=initial_payload)
                
#                 if response.status_code != 200:
#                     print(f"Erro na requisição inicial para {shipment_number}: {response.text}")
#                     continue

#                 data = response.json().get("data", {})
#                 total_pages = data.get("pages", 0)
                
#                 if total_pages < 1:
#                     print(f"Sem páginas para {shipment_number}.")
#                     continue
                
#                 # Iterar sobre as páginas
#                 for i in range(1, total_pages + 1):
#                     page_payload = {**initial_payload, "current": i}
#                     print(f"Requisitando página {i}/{total_pages} para {shipment_number}...")
#                     page_response = requests.post(url=url, headers=header, json=page_payload)
                    
#                     if page_response.status_code != 200:
#                         print(f"Erro na página {i} para {shipment_number}: {page_response.text}")
#                         continue
                    
#                     page_data = page_response.json().get("data", {}).get("records", [])
#                     self.final_wb += page_data
#                     os.system("cls")
#                     print(f"Recebidos {len(page_data)} registros na página {i} para {shipment_number}.")
#                     # Processar os dados da página aqui
#             except Exception as e:
#                 print(f"Erro inesperado para {shipment_number}: {e}")







# JMS_Report("920b3f10865d4a06a3f689b5c83ea904").fetch_data()


import aiohttp
import asyncio
import datetime
import pandas as pd
import os

class JMS_Report:
    def __init__(self, authtoken):
        self.authtoken = authtoken
        self.start_date = (datetime.datetime.today() - datetime.timedelta(1)).strftime("%Y-%m-%d")
        self.end_date = (datetime.datetime.today() + datetime.timedelta(0)).strftime("%Y-%m-%d")
        self.transport_ids = []
        self.final_wb = []

    async def sc_transport_id(self, session): 
        # 
        url = f"https://gw.jtjms-br.com/transportation/tmsShipment/page?current=1&size=999&startCode=31101&startDateTime={self.start_date}+15:00:00&endDateTime={self.end_date}+15:00:00&searchType=manage"
        headers = {"authToken": self.authtoken}
        
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                records = data.get("data", {}).get("records", [])
                for record in records:

                    plannedArrivalCheck = datetime.datetime.today().strftime("%Y-%m-%d 23:59:59")
                    plannedArrivalCheck = datetime.datetime.strptime(plannedArrivalCheck, "%Y-%m-%d %H:%M:%S")
                    plannedArrival = datetime.datetime.strptime(record["plannedArrivalTime"], "%Y-%m-%d %H:%M:%S")


                    if record["shipmentState"] in [3, 4] and record["startName"] in ["SC BRE 01"] and record["endName"] in ["SC BSB 01", "SC CGE 02", "SC SJM 01", "DC SRR 001"] and plannedArrival < plannedArrivalCheck:
                        self.transport_ids.append([record["shipmentNo"], record["createTime"]])
            else:
                print(f"Erro na resposta SC: {response.status}")

    async def dc_transport_id(self, session): # Não necessita de alteração
        url = "https://gw.jtjms-br.com/transportation/tmsBranchTrackingDetail/page"
        headers = {"authToken": self.authtoken}
        today = datetime.datetime.today().strftime("%Y-%m-%d")
        tomorrow = (datetime.datetime.today() + datetime.timedelta(1)).strftime("%Y-%m-%d")
        payloads = [
            {"current": 1, "size": 100, "startDepartureTime": f"{today} 00:00:00", "endDepartureTime": f"{today} 23:59:59", "endCode": "316001", "countryId": "1"},
            {"current": 1, "size": 100, "startDepartureTime": f"{today} 00:00:00", "endDepartureTime": f"{today} 23:59:59", "endCode": "535105", "countryId": "1"},
            {"current": 1, "size": 100, "startDepartureTime": f"{today} 06:00:00", "endDepartureTime": f"{tomorrow} 06:00:00", "endCode": "535104", "countryId": "1"}
        ]
        
        for payload in payloads:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    records = data.get("data", {}).get("records", [])
                    for record in records:
                        # if record["shipmentState"] in [2, 3, 4]:
                            self.transport_ids.append([record["shipmentNo"], record["createTime"]])
                else:
                    print(f"Erro na resposta DC: {response.status}")

    async def fetch_data(self):
        async with aiohttp.ClientSession() as session:
            await self.sc_transport_id(session)
            await self.dc_transport_id(session)
            # print(self.transport_ids)
            # breakpoint()
            wb_header = ["Número de pedido JMS", "Número do lote", "Chip No.", "Tipo de bipagem", "Tempo de digitalização", "Base de escaneamento", "Parada anterior ou próxima", "Saída do dia", "Quantidade de volumes", "Peso", "Tipo de peso", "Tipo de produto", "Modal", "Estação de origem", "Nome do Cliente", "Digitalizador", "Digitalizador No.", "Correio de coleta ou entrega", "Número de correio de coleta ou entrega", "Signatário", "Origem de dados", "Observação", "Tempo de upload", "Dispositivo No.", "Celular No.", "Comprimento", "Largura", "Altura", "Peso volumétrico", "CEP de origem", "CEP destino", "Número do ID", "Selo de veículo", "Nome da linha", "Reserva No,", "Tipo problemático", "Descrição da não conformidade", "Tipos de pacote não expedido", "Descrição de pacotes não expedidos", "Contato da área de agência", "Endereço da área de agência", "Município de Destino", "Estado da cidade de destino", "PDD de chegada", "Nome do cliente", "Peso Faturado"]
            url = "https://gw.jtjms-br.com/operatingplatform/scanRecordQuery/listPage"
            headers = {"authToken": self.authtoken, "lang": "PT", "langType": "PT",}
            base_payload = {
                "current": 1,
                "size": 999,
                "startDates": "",
                "endDates": "",
                "scanSite": "31101",
                "scanType": "装车扫描",
                "transferCode": "",
                "sortName": "scanDate",
                "sortOrder": "asc",
                "bilNos": [],
                "querySub": "querySub",
                "reachAddressList": [],
                "sendSites": [],
                "billType": 1,
                "countryId": "1"
            }

            tasks = []
            for shipment_number, start_date in self.transport_ids:
                tasks.append(self.process_shipment(session, url, headers, base_payload, shipment_number, start_date))
            await asyncio.gather(*tasks)

            df = pd.DataFrame(self.final_wb)
            df.to_csv("teste.csv", index = False, header = wb_header,sep = ";", encoding = "utf-8-sig")

    async def process_shipment(self, session, url, headers, base_payload, shipment_number, start_date):
        try:
            start_date_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
            end_date_dt = start_date_dt + datetime.timedelta(days=4)
            initial_payload = {
                **base_payload,
                "startDates": start_date_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "endDates": end_date_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "transferCode": shipment_number
            }

            async with session.post(url, headers=headers, json=initial_payload) as response:
                if response.status != 200:
                    print(f"Erro inicial para {shipment_number}: {response.status}")
                    return

                data = await response.json()
                total_pages = data.get("data", {}).get("pages", 0)
                
                for i in range(1, total_pages + 1):
                    page_payload = {**initial_payload, "current": i}
                    async with session.post(url, headers=headers, json=page_payload) as page_response:
                        if page_response.status != 200:
                            print(f"Erro na página {i} para {shipment_number}: {page_response.status}")
                            continue

                        page_data = await page_response.json()
                        records = page_data.get("data", {}).get("records", [])
                        # self.final_wb += records
                        for record in records:
                            # print(record["billNo"], record["listNo"], record["belongNo"], record["scanType"], record["scanDate"], record["inputDept"], record["upOrNextStation"], record["banCi"], record["piece"], record["weight"], record["weightType"], record["goodsType"], record["expreeType"], record["sendSite"], record["sendCus"], record["scanEmp"], record["employeeCode"], record["dispatchReciper"], record["deliveryCode"], record["signUser"], record["dataSource"], record["remark"], record["inputDate"], record["baGunId"], record["phone"], record["length"], record["width"], record["height"], record["bulkWeight"], record["senderPostalCode"], record["receiverPostalCode"], record["transferCode"], record["carSealingLead"], record["carNumber"], record["bookingNo"], record["difficultType"], record["difficultDescription"], record["stayType"], record["stayDescription"], "", "", record["receiverCityName"], record["receiverProvinceName"], record["dispatchNetworkName"], record["customerName"], record["packageChargeWeight"])
                            self.final_wb.append({
                                "billNo": record["billNo"],
                                "listNo": record["listNo"],
                                "belongNo": record["belongNo"],
                                "scanType": record["scanType"],
                                "scanDate": record["scanDate"],
                                "inputDept": record["inputDept"],
                                "upOrNextStation": record["upOrNextStation"],
                                "banCi": record["banCi"],
                                "piece": record["piece"],
                                "weight": record["weight"],
                                "weightType": record["weightType"],
                                "goodsType": record["goodsType"],
                                "expreeType": record["expreeType"],
                                "sendSite": record["sendSite"],
                                "sendCus": record["sendCus"],
                                "scanEmp": record["scanEmp"],
                                "employeeCode": record["employeeCode"],
                                "dispatchReciper": record["dispatchReciper"],
                                "deliveryCode": record["deliveryCode"],
                                "signUser": record["signUser"],
                                "dataSource": record["dataSource"],
                                "remark": record["remark"],
                                "inputDate": record["inputDate"],
                                "baGunId": record["baGunId"],
                                "phone": record["phone"],
                                "length": record["length"],
                                "width": record["width"],
                                "height": record["height"],
                                "bulkWeight": record["bulkWeight"],
                                "senderPostalCode": record["senderPostalCode"],
                                "receiverPostalCode": record["receiverPostalCode"],
                                "transferCode": record["transferCode"],
                                "carSealingLead": record["carSealingLead"],
                                "carNumber": record["carNumber"],
                                "bookingNo": record["bookingNo"],
                                "difficultType": record["difficultType"],
                                "difficultDescription": record["difficultDescription"],
                                "stayType": record["stayType"],
                                "stayDescription": record["stayDescription"],
                                "TESTE": "",
                                "TESTE2": "",
                                "receiverCityName": record["receiverCityName"],
                                "receiverProvinceName": record["receiverProvinceName"],
                                "dispatchNetworkName": record["dispatchNetworkName"],
                                "customerName": record["customerName"],
                                "packageChargeWeight": record["packageChargeWeight"]
                            })

                        print(f"Recebidos {len(records)} registros na página {i} para {shipment_number}.")
        except Exception as e:
            print(f"Erro inesperado para {shipment_number}: {e}")

# Iniciar o processo
if __name__ == "__main__":
    authtoken = "b600b8a9963444b5bcccd6c3de6a0e69"
    report = JMS_Report(authtoken)
    asyncio.run(report.fetch_data())
