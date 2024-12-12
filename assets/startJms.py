from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import os
import datetime
from time import sleep
import json
import threading
import sys
import requests
import pandas as pd
import asyncio

from tkinter import messagebox
from assets.CaptchaSolver.captcha_solver import CaptchaSolverYOLO
from assets.volumetry_report2 import JMS_Report

# # Logar no JMS e retornar informações continas nos Cookies(localStorage) "YL_TOKEN" e "userData"
class ProjetoJMS():
    def __init__(self):

        self.userData = None
        self.authToken = None

        self.url = 'https://jmsbr.jtjms-br.com/login'

        self.todayDate = datetime.datetime.today().strftime("%Y-%m-%d")

        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--disable-blink-features=AutomationControlled") 
        self.options.add_argument("--ignore-certificate-errors")
        self.options.add_argument("--timeout=120")
        self.options.add_argument("--window-position=0,0")
        self.options.add_argument("--window-size=800,600")

        self.options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
        self.options.add_experimental_option("useAutomationExtension", False)
        self.downloadDir = os.path.join(os.path.expanduser('~'),'Downloads')
        prefs = {"profile.default_content_settings.popups": 0,    
        "download.default_directory": self.downloadDir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True}

        self.options.add_experimental_option("prefs",prefs)
        user_data_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Google", "Chrome", "User Data", "Conta BRE")
        self.options.add_argument(f"user-data-dir={user_data_dir}")

        self.driver = webdriver.Chrome(options=self.options)
        self.driver.get(self.url)

    def extractCookies(self):
        userData = self.driver.execute_script("return localStorage.getItem('userData')")
        userData = json.loads(userData)
        authToken = self.driver.execute_script("return localStorage.getItem('YL_TOKEN')")        
        return userData.get("staffNo",""), authToken

    def start(self):
        sleep(5)
        with open(os.path.join("assets","settings.json"), "r", encoding = "utf-8") as file:
            creds = json.load(file)

        while self.driver.current_url == self.url:
            sleep(5)
            CaptchaSolverYOLO().login(self.driver, creds["login"], creds["password"])
            if self.driver.current_url != self.url:
                break

        self.userData, self.authToken = self.extractCookies()

        if self.userData and self.authToken:

            # self.driver.set_window_size(1, 1)
            # self.driver.minimize_window()
            self.driver.quit()


            asyncio.run(JMS_Report(self.authToken).fetch_data())

            # shipmentInfo = []

            # volumetria = []
            # for shipmentID in volumetriaJms.getShipmentIDs():
            #     shipmentInfo.append(volumetriaJms.getShipmentInfo(shipmentID))

            # for info in shipmentInfo:
            #     for order in volumetriaJms.getOrders(info[0], info[1], info[2], info[3]):
            #         volumetria.append(order)


            # # Verificar ultima data de modificação do arquivo e verficar se é dia da semana
            # # Caminho para o arquivo
            # file_path = os.path.join("D:/BI Planejamento/BI 1.1/Previsão de volumetria","BRE.csv")
            # if os.path.exists(file_path):
            #     # Obtendo o horário de modificação como timestamp
            #     timestamp_modificacao = os.path.getmtime(file_path)

            #     # Convertendo o timestamp para um objeto datetime
            #     horario_modificacao = datetime.datetime.fromtimestamp(timestamp_modificacao)

            #     # Formatando o horário de modificação
            #     horario_modificacao_formatado = horario_modificacao.strftime("%d-%m-%Y")
            #     hoje = (datetime.datetime.today()).strftime("%d-%m-%Y")
                
            #     if horario_modificacao_formatado < hoje and datetime.datetime.today().weekday() not in [5,6]:
            #         os.remove(file_path)

            # os.makedirs("D:/BI Planejamento/BI 1.1/Previsão de volumetria", exist_ok = True)

            # df = pd.DataFrame(volumetria)
            # if os.path.exists(file_path):
            #     df.to_csv(file_path,sep = ";", encoding = "utf-8-sig", header = True, index = False, mode = "a")
            # else:
            #     header = ["Número do Pedido JMS", "SC Origem", "SC Destino", "Lote No.", "Tempo de Escaneamento", "Total", "Base Destino", "Cidade Destino", "ID Viagem", "Tempo Previsto de Chegada"]
            #     df.to_csv(file_path,sep = ";", encoding = "utf-8-sig", header = header, index = False)

        else:
            sys.exit()

# ProjetoJMS().start()