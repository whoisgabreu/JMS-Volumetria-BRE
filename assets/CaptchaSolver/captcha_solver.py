#PyAutoGui
import os
# Numpy/cv2
import numpy as np
import cv2
# Selenium/Webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
import os
from webdriver_manager.chrome import ChromeDriverManager
import time
import cv2
from ultralytics import YOLO

class CaptchaSolverYOLO():

    def captcha_solver(self, img_path):

        model_path = os.path.join(os.path.dirname(__file__),"best.pt")

        model = YOLO(model_path)

        img = cv2.imread(img_path)

        results = model(img)

        piece = None
        slot = None

        for result in results:
            boxes = result.boxes
            for box in boxes:
                class_id = int(box.cls[0])

                label = f"{model.names[class_id]}"
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                if label == "piece":
                    piece = x1

                if label == "slot":
                    slot = x1

        return slot-piece

    def login(self,driver,user:str,password:str):
        action = ActionChains(driver)
        try:
            print("Inserindo login")
            driver.find_elements(By.CSS_SELECTOR,'input[class="el-input__inner"]')[1].send_keys(Keys.CONTROL,'a')
            driver.find_elements(By.CSS_SELECTOR,'input[class="el-input__inner"]')[1].send_keys(user)
            driver.find_elements(By.CSS_SELECTOR,'input[class="el-input__inner"]')[2].send_keys(Keys.CONTROL,'a')
            driver.find_elements(By.CSS_SELECTOR,'input[class="el-input__inner"]')[2].send_keys(password)
            driver.find_elements(By.CSS_SELECTOR,'input[class="el-input__inner"]')[1].click()
            driver.find_elements(By.CSS_SELECTOR,'button[class="el-button el-button--primary el-button--small login-btn"]')[0].click()
            print("Alternando para iFrame Captcha")
            time.sleep(5)
            driver.switch_to.frame("https://sg.captcha.qcloud.com")
            img = driver.find_element(By.XPATH,'//img[@class="tc-bg-placeholder"]')
            with open(f'captcha-{user}.png', 'wb') as file:
                file.write(img.screenshot_as_png)
            
            print("Salvando Screenshot")
            driver.switch_to.default_content()

            coord = self.captcha_solver(f'captcha-{user}.png')
            print(coord)

            driver.switch_to.frame("tcaptcha_iframe_dy")
            
            slider = WebDriverWait(driver,6000, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="tc-fg-item tc-slider-normal"]')))
            action.move_to_element(slider).click_and_hold().move_by_offset(coord,0).perform()
            
            time.sleep(1)
            action.release().perform()
            time.sleep(5)
            try:
                driver.execute_script('document.getElementsByClassName("tc-action tc-icon tc-action--close")[0].click();')
            except:
                pass
            driver.switch_to.default_content()
        except:
            driver.execute_script('document.getElementsByClassName("tc-action tc-icon tc-action--close")[0].click();')
            driver.switch_to.default_content()