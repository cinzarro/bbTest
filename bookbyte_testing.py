import os
import threading
import time
import unittest
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located

class TestRequest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        chrome_options = Options()
        chrome_options.add_argument("--headless")

        cls.driver = webdriver.Chrome(options=chrome_options)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    #a test to ensure google.com is working
    #def test_request(self):
    #    wait = WebDriverWait(self.driver, 10)
    #    self.driver.get("https://google.com/ncr")
    #    self.driver.find_element(By.NAME,"q").send_keys("cheese" + Keys.RETURN)
    #    first_result = wait.until(presence_of_element_located((By.XPATH, "//div[@aria-label='Show more']")))
    #    self.assertEqual('Show more', first_result.get_attribute("textContent"))

    #Scneario 1: Verify Bookyte's Seller Profile address is "2800 Pringle Rd SE Suite 100"
    def test_bookbyte_amazon_address(self):
        print()
        self.driver.get("https://www.amazon.com/sp?seller=A2N51X1QYGFUPK")
        wait = WebDriverWait(self.driver, 10)
        addressXpath = "//div[@id='seller-profile-container']//span[.='Business Address:']/following-sibling::ul/li[position()=1]/span"
        wait.until(presence_of_element_located((By.XPATH, addressXpath)))
        addressSpan = self.driver.find_element(By.XPATH, addressXpath)

        expected = "2800 Pringle Rd SE Suite 100"
        actual = addressSpan.get_attribute('textContent')

        print("Scenario 1: Verifying expected (" + expected + ") vs actual (" + actual + ")")
        self.assertEqual(expected, actual)

    #Scenario 2: Verify Result page title is "C Programming Language, 2nd Edition" after using Bookbyte's advanced search page to find ISBN 0131103628
    def test_bookbyte_advanced_search_functionality(self):
        print()
        self.driver.get("https://www.bookbyte.com/advancedsearch.aspx")
        wait = WebDriverWait(self.driver, 10)

        isbnXpath = "//input[@type='text' and contains(@id, 'ISBN')]"
        wait.until(presence_of_element_located((By.XPATH, isbnXpath)))
        isbnInput = self.driver.find_element(By.XPATH, isbnXpath)
        isbnInput.clear()
        isbnInput.send_keys("0131103628")

        searchButtonXpath = "//input[@type='image' and contains(@name, 'Search')]"
        wait.until(presence_of_element_located((By.XPATH, searchButtonXpath)))
        self.driver.find_element(By.XPATH, searchButtonXpath).send_keys(Keys.ENTER)

        resultTitleXpath = "//span[contains(@id, 'lbTitle')]"
        wait.until(presence_of_element_located((By.XPATH, resultTitleXpath)))

        expected = "C Programming Language, 2nd Edition"
        actual = self.driver.find_element(By.XPATH, resultTitleXpath).get_attribute('textContent')

        print("Scenario 2: Verifying expected (" + expected + ") vs actual (" + actual + ")")
        self.assertEqual(expected, actual)

    #Scenario 3: Verify Google Books API - Request book ISBN "0131103628" authors "Brian W. Kernighan" & "Dennis M. Ritchie"
    def test_google_book_api_book_search(self):
        print()
        targetISBN = "0131103628"
        bookTitle = "The C Programming Language"
        expectedAuthors = ["Brian W. Kernighan", "Dennis M. Ritchie"]
        
        print("Scenario 3: Expected Authors: " + ", ".join(expectedAuthors))
        
        response = requests.get('https://www.googleapis.com/books/v1/volumes?q=isbn+' + targetISBN)

        response.raise_for_status()
        responseJson = response.json()

        if len(responseJson) > 0:
             items = responseJson['items']
             for item in items:
                 volumeInfo = item['volumeInfo']
                 if volumeInfo['title'] == bookTitle:
                     for author in expectedAuthors:
                         print("  Verifying author " + author + " is attributed")
                         self.assertTrue(author in volumeInfo['authors'])
        else:
            raise RequestException("Unexpected results from request")

if __name__ == '__main__':
    unittest.main()
    #print ("all done tests ran")
