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

    async def dc_transport_id(self, session):
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
                        self.transport_ids.append([record["shipmentNo"], record["createTime"]])
                else:
                    print(f"Erro na resposta DC: {response.status}")

    async def fetch_data(self):
        async with aiohttp.ClientSession() as session:
            await self.sc_transport_id(session)
            await self.dc_transport_id(session)

            wb_header = ["Número de pedido JMS", "Número do lote", "Chip No.", "Tipo de bipagem", "Tempo de digitalização", "Base de escaneamento", "Parada anterior ou próxima", "Saída do dia", "Quantidade de volumes", "Peso", "Tipo de peso", "Tipo de produto", "Modal", "Estação de origem", "Nome do Cliente", "Digitalizador", "Digitalizador No.", "Correio de coleta ou entrega", "Número de correio de coleta ou entrega", "Signatário", "Origem de dados", "Observação", "Tempo de upload", "Dispositivo No.", "Celular No.", "Comprimento", "Largura", "Altura", "Peso volumétrico", "CEP de origem", "CEP destino", "Número do ID", "Selo de veículo", "Nome da linha", "Reserva No,", "Tipo problemático", "Descrição da não conformidade", "Tipos de pacote não expedido", "Descrição de pacotes não expedidos", "Contato da área de agência", "Endereço da área de agência", "Município de Destino", "Estado da cidade de destino", "PDD de chegada", "Nome do cliente", "Peso Faturado"]
            url = "https://gw.jtjms-br.com/operatingplatform/scanRecordQuery/listPage"
            headers = {"authToken": self.authtoken, "lang": "PT", "langType": "PT"}
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

            tasks = [self.process_shipment(session, url, headers, base_payload, sn, sd) for sn, sd in self.transport_ids]
            await asyncio.gather(*tasks)

            df = pd.DataFrame(self.final_wb)
            df.to_csv("teste.csv", index=False, header=wb_header, sep=";", encoding="utf-8-sig")

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
                        for record in records:
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
