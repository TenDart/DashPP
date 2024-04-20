import requests
import time
from selenium import webdriver as wd
from selenium.webdriver.common.by import By
options = wd.ChromeOptions()
options.add_argument('--no-sandbox')
url = "https://www.samcodes.co.uk/project/geometrize-haxe-web/"
driver = wd.Chrome(options= options)
driver.get(url)
#start()
driver.implicitly_wait(3)
driver.find_element( By.XPATH, '/html/body/section[2]/div/h2/label' ).click()
firstConvertion = True
def convertFileToJSON(filePath:str):
    global driver, firstConvertion
    driver.find_element(By.ID, "openimageinput").send_keys(filePath)
    if firstConvertion == False:
        driver.find_element(By.ID, "resetbutton").click()
        driver.find_element(By.ID, "runpausebutton").click()
    else:
        firstConvertion = True
    while True:
        if driver.find_element(By.ID, "shapesaddedtext").text != "":
            if int(driver.find_element(By.ID, "shapesaddedtext").text) > 150:
                print("huh")
                driver.find_element(By.ID, "savejsonbutton").click()
                break
counter = int(200)
for i in range(100):
    convertFileToJSON(r"D:\DevThings\CPPprojects\VisualStudio\Ddash++\rawFrames\masayoshi-minoshima-bad-apple_311366_" + str(counter) + ".jpg")
    counter += 1
#geometrizeToGd("geometrized_json (9).json")     # heyheyhey
#imageToGd("New Piskel.png")rfffff
#end()
#int(driver.find_element(By.ID, "shapesaddedtext").text)
while True:
    pass
driver.quit()