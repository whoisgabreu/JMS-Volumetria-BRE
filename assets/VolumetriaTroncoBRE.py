import requests
import datetime
import pandas as pd
import os
import time
from .update_appefficiency_info import update_appefficiency_info
import random


class VolumetriaJMS:
    
    def __init__(self, authToken) -> None:
        self.authToken = authToken
        self.dataInicio = (datetime.datetime.today() - datetime.timedelta(days = 4)).strftime("%Y-%m-%d")
        self.horaInicio = (datetime.datetime.today() - datetime.timedelta(hours = 3)).strftime("%H:%M:%S")
        self.dataFim = (datetime.datetime.today()).strftime("%Y-%m-%d")
    ## 1° PASSO
    # Requisição do tipo GET para pesquisar todos os IDs de viagem
    #                                                                                             {START DATE}                    {END DATE}
    # https://gw.jtjms-br.com/transportation/tmsShipment/page?current=1&size=999999&startDateTime=2024-07-31+00:00:00&endDateTime=2024-08-01+23:59:59&searchType=manage
    # Filtrar ID de viagem usando a chave ["shipmentState"] se for 3 e 4 (Em transito e Concluído. Respectivamente)
    # Analisar horário previsto de chegada se baseando no horário planejado de saída > (["plannedDepartureTime"] + tempo de viagem)

    # Se a viagem estiver dentro dos padrões especificados 'appendar'
    # informações necessárias do ID à uma lista que será utilizada no 2° passo

    def getShipmentIDs(self):
        
        print("getShipmentIDs")
        shipmentID = []

        url = f"https://gw.jtjms-br.com/transportation/tmsShipment/page?current=1&size=999999&startDateTime={self.dataInicio}+00:00:00&endDateTime={self.dataFim}+23:59:59&searchType=manage"

        header = {
            'Accept' : 'application/json, text/plain, */*',
            'Accept-Encoding' : 'gzip, deflate, br, zstd',
            'Accept-Language' : 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7,de;q=0.6',
            'Cache-Control' : 'max-age=2, must-revalidate',
            'Connection' : 'keep-alive',
            'Content-Type' : 'application/json;charset=utf-8',
            'Host' : 'gw.jtjms-br.com',
            'Origin' : 'https',
            'Referer' : 'https',
            'Sec-Fetch-Dest' : 'empty',
            'Sec-Fetch-Mode' : 'cors',
            'Sec-Fetch-Site' : 'same-site',
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
            'authToken' : self.authToken,
            'lang' : 'PT',
            'langType' : 'PT',
            'routeName' : 'monitoringSearch',
            'sec-ch-ua' : '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            'sec-ch-ua-mobile' : '?0',
            'sec-ch-ua-platform' : '"Windows"',
            'timezone' : 'GMT-0300'
        }

        resultado = requests.get(url = url, headers = header)

        for record in resultado.json()["data"]["records"]:
            if record["shipmentState"] in [3,4] and record["endName"] in ["SC CGE 02", "SC BSB 01", "SC RAO 01", "SC SJM 01"]:
                shipmentID.append([record["shipmentNo"], record["plannedArrivalTime"]])

        return shipmentID

    # ======================================================================================================
    ## 2° PASSO
    # Requisição do tipo GET para pesquisar informações sobre o ID
    # https://gw.jtjms-br.com/transportation/trackingDeatil/loading/scan/list?shipmentNo={ID DA VIAGEM AQUI}
    # Pegar as informações necessárias para o 3° passo

    def getShipmentInfo(self, travelId):
        print("getShipmentInfo")
        url = f"https://gw.jtjms-br.com/transportation/trackingDeatil/loading/scan/list?shipmentNo={travelId[0]}"

        header = {
            'Accept' : 'application/json, text/plain, */*',
            'Accept-Encoding' : 'gzip, deflate, br, zstd',
            'Accept-Language' : 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7,de;q=0.6',
            'Cache-Control' : 'max-age=2, must-revalidate',
            'Connection' : 'keep-alive',
            'Content-Type' : 'application/json;charset=utf-8',
            'Host' : 'gw.jtjms-br.com',
            'Origin' : 'https',
            'Referer' : 'https',
            'Sec-Fetch-Dest' : 'empty',
            'Sec-Fetch-Mode' : 'cors',
            'Sec-Fetch-Site' : 'same-site',
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
            'authToken' : self.authToken,
            'lang' : 'PT',
            'langType' : 'PT',
            'routeName' : 'monitoringSearchLoading',
            'sec-ch-ua' : '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            'sec-ch-ua-mobile' : '?0',
            'sec-ch-ua-platform' : '"Windows"',
            'timezone' : 'GMT-0300'
        }

        resultado = requests.get(url = url, headers = header)

        for data in resultado.json()["data"]:
            if data["scanNetworkName"] == "SC BRE 01":
                return (data["jobCode"], data["scanNetworkCode"], data["scanWaybillNum"], travelId[1])


    # ======================================================================================================
    ## 3° PASSO
    #                                                                                                            ["jobCode"]                      ["scanNetworkCode"]                  ["scanWaybillNum"]
    # https://gw.jtjms-br.com/transportation/trackingDeatil/loading/scan/page?current=1&size=999999&shipmentNo={ID DA VIAGEM}&scanNetworkCode={CODIGO DA BASE ESCANEADORA}&countNum={QNTD DE PEÇAS BIPADAS}

    # Realizar pesquisas para cada um dos IDs coletados e criar planilha consolidada com todos os dados
    # (De preferência carregar uma planilha existente e incluir os dados)
    def getOrder(self, jobCode, scanNetworkCode, waybillNum, Arrival):
        print("getOrder")
        url = "https://gw.jtjms-br.com/operatingplatform/scanRecordQuery/listPage"

        header = {
            'Accept' : 'application/json, text/plain, */*',
            'Accept-Encoding' : 'gzip, deflate, br, zstd',
            'Accept-Language' : 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7,de;q=0.6',
            'Cache-Control' : 'max-age=2, must-revalidate',
            'Connection' : 'keep-alive',
            'Content-Length' : '301',
            'Content-Type' : 'application/json;charset=UTF-8',
            'Host' : 'gw.jtjms-br.com',
            'Origin' : 'https',
            'Referer' : 'https',
            'Sec-Fetch-Dest' : 'empty',
            'Sec-Fetch-Mode' : 'cors',
            'Sec-Fetch-Site' : 'same-site',
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
            'authToken' : self.authToken,
            'lang' : 'PT',
            'langType' : 'PT',
            'routeName' : 'scanQueryConstantlyNew',
            'sec-ch-ua' : '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            'sec-ch-ua-mobile' : '?0',
            'sec-ch-ua-platform' : '"Windows"',
            'timezone' : 'GMT-0300'
        }

        payload = {
            "current": 1,
            "size": 100,
            "startDates": self.dataInicio,
            "endDates": self.dataFim,
            "scanSite": scanNetworkCode,
            "scanType":"装车扫描",
            "transferCode": jobCode,
            "sortName": "scanDate",
            "sortOrder": "asc",
            "bilNos": [],
            "querySub": "",
            "reachAddressList": [],
            "sendSites": [],
            "billType": 1,
            "countryId": "1"}

        results = requests.post(url = url, headers = header, json = payload)

        # FINALIZAR SEGUNDA-FEIRA
        records = []
        pages = results.json()["data"]["pages"]
        for page in range(1, pages):

            payload = {
            "current": page,
            "size": 100,
            "startDates": self.dataInicio,
            "endDates": self.dataFim,
            "scanSite": scanNetworkCode,
            "scanType":"装车扫描",
            "transferCode": jobCode,
            "sortName": "scanDate",
            "sortOrder": "asc",
            "bilNos": [],
            "querySub": "",
            "reachAddressList": [],
            "sendSites": [],
            "billType": 1,
            "countryId": "1"
            }

            results = requests.post(url = url, headers = header, json = payload)

            for item in results.json()["data"]["records"]:
                records.append([item["billNo"],item["inputDept"],item["upOrNextStation"],item["dispatchNetworkName"],item["receiverCityName"],item["transferCode"],item["customerName"],item["sendSite"],item["receiverPostalCode"], Arrival])

        
        return records

    def start(self):
        shipmentInfo = []
        volumetria = []

        start_time = time.perf_counter()
        
        # Obter IDs de remessa
        for shipmentID in self.getShipmentIDs():
            shipmentInfo.append(self.getShipmentInfo(shipmentID))

        # Obter informações dos pedidos
        for info in shipmentInfo:
            for order in self.getOrder(info[0], info[1], info[2], info[3]):
                volumetria.append(order)

        # Caminho para o arquivo
        file_path = os.path.join("C:/BI Planejamento/BI 2.0/Previsão de volumetria", "BRE.csv")

        # Verificar a última data de modificação do arquivo e remover se for um novo dia útil
        if os.path.exists(file_path):
            timestamp_modificacao = os.path.getmtime(file_path)
            horario_modificacao = datetime.datetime.fromtimestamp(timestamp_modificacao)
            horario_modificacao_formatado = horario_modificacao.strftime("%d-%m-%Y")
            hoje = datetime.datetime.today().strftime("%d-%m-%Y")

            if horario_modificacao_formatado < hoje and datetime.datetime.today().weekday() not in [5, 6]:
                os.remove(file_path)

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Criar DataFrame a partir dos dados obtidos
        df_volumetria = pd.DataFrame(volumetria)
        if os.path.exists(file_path):
            # Carregar dados existentes do arquivo CSV
            df_existente = pd.read_csv(file_path, sep=";", encoding="utf-8-sig")

            # Verificar se o cabeçalho está presente
            if "Número do Pedido JMS" not in df_volumetria.columns:
                df_volumetria.columns = df_existente.columns

            # Comparar a primeira coluna ("Número do Pedido JMS")
            novos_numeros_pedidos = ~df_volumetria['Número do Pedido JMS'].isin(df_existente['Número do Pedido JMS'])

            # Filtrar novos registros com base na primeira coluna
            df_novos = df_volumetria[novos_numeros_pedidos]

            # Adicionar novos registros, se houver
            if not df_novos.empty:
                df_novos.to_csv(file_path, sep=";", encoding="utf-8-sig", header=False, index=False, mode="a")
        else:
            # Se o arquivo não existir, criar com cabeçalhos
            header = ["Número do Pedido JMS", "Base de escaneamento", "Parada anterior ou próxima", "PDD de chegada", "Município de Destino", "Número do ID", "Nome do cliente", "Estação de origem", "CEP destino"]
            df_volumetria.columns = header
            df_volumetria.to_csv(file_path, sep=";", encoding="utf-8-sig", header=True, index=False)

        final_time = round((time.perf_counter() - start_time) / 60, 2)

        rand_time = random.randint(1,6)
        time.sleep(rand_time)
        update_appefficiency_info("volumetry-report", final_time = final_time, quantity = 1)