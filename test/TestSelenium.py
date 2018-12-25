from selenium import webdriver
import time


def openAndInput():
    driver = webdriver.Chrome()
    driver.get("http://www.baidu.com")
    input_place = driver.find_element_by_id("kw")
    time.sleep(2)
    input_place.send_keys("selenium")
    time.sleep(1)
    button = driver.find_element_by_css_selector("#su")
    button.click()
    time.sleep(10)


if __name__ == '__main__':
    openAndInput()
