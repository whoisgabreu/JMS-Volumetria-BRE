#PyAutoGui
import pyautogui
from pyautogui import *
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

class Coord():
    def __init__(self) -> None:
        # Images
        self.slider_img = cv2.imread(r"assets/Captcha_Solver/patterns2/slider.png", cv2.IMREAD_GRAYSCALE)
        self.puzzle_imgs = [
                            cv2.imread(r"assets/Captcha_Solver/patterns\puzzlePattern.png", cv2.IMREAD_GRAYSCALE),
                            cv2.imread(r"assets/Captcha_Solver/patterns\puzzlePattern2.png", cv2.IMREAD_GRAYSCALE),
                            cv2.imread(r"assets/Captcha_Solver/patterns\puzzlePattern3.png", cv2.IMREAD_GRAYSCALE)
                            ]

    def find_coord(self,screenshot_path:str):

            screenshot = cv2.imread(screenshot_path,cv2.IMREAD_GRAYSCALE)

            # Localizar Slide
            slider_match = cv2.matchTemplate(screenshot,self.slider_img, cv2.TM_CCOEFF_NORMED)
            a,b,c, slider_max_loc = cv2.minMaxLoc(slider_match)
            slider_x,slider_y = slider_max_loc

            for puzzle_img in self.puzzle_imgs:
                # Localiza o puzzle
                puzzle_match = cv2.matchTemplate(screenshot,puzzle_img,cv2.TM_CCOEFF_NORMED)
                a,b,c,puzzle_max_loc = cv2.minMaxLoc(puzzle_match)
                puzzle_x,puzzle_y = puzzle_max_loc

                if puzzle_match.max() > 0.75:
                    break

            if slider_match.max() > 0.75 and puzzle_match.max() > 0.75:
                # Calcula a diferença entre X e Y entre o Slide e o Puzzle
                if abs(puzzle_x - slider_x) > 24 and abs(puzzle_x - slider_x) != 277:
                    result = abs(slider_x - puzzle_x)

                    return result

        
    def login(self,driver,user:str,password:str,screenshot_path:str):

        action = ActionChains(driver)

        try:

            driver.find_elements(By.CSS_SELECTOR,'input[class="el-input__inner"]')[1].send_keys(Keys.CONTROL,'a')
            driver.find_elements(By.CSS_SELECTOR,'input[class="el-input__inner"]')[1].send_keys(user)
            driver.find_elements(By.CSS_SELECTOR,'input[class="el-input__inner"]')[2].send_keys(Keys.CONTROL,'a')
            driver.find_elements(By.CSS_SELECTOR,'input[class="el-input__inner"]')[2].send_keys(password)
            driver.find_elements(By.CSS_SELECTOR,'input[class="el-input__inner"]')[1].click()
            driver.find_elements(By.CSS_SELECTOR,'button[class="el-button el-button--primary el-button--small login-btn"]')[0].click()

            driver.switch_to.frame("tcaptcha_iframe_dy")
            time.sleep(5)

            driver.save_screenshot(screenshot_path)
            time.sleep(5)

            coord = None

            while coord == None:
                driver.execute_script('document.getElementsByClassName("tc-button-icon tc-refresh-icon")[0].click();')
                time.sleep(5)
                driver.save_screenshot(screenshot_path)
                time.sleep(5)
                coord = self.find_coord(screenshot_path)

            time.sleep(2)
            slider = WebDriverWait(driver,6000, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="tc-fg-item tc-slider-normal"]')))
            action.move_to_element(slider).click_and_hold().move_by_offset(coord-12,0).release().perform()
            time.sleep(5)

            try:
                driver.execute_script('document.getElementsByClassName("tc-close-icon")[0].click();')

            except: pass

            driver.switch_to.default_content()

        except:
            driver.execute_script('document.getElementsByClassName("tc-close-icon")[0].click();')
            driver.switch_to.default_content()