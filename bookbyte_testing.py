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
from selenium.webdriver.support import expected_conditions as EC

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
    def test_request(self):
        print() #prettify output
        print("Scenario 0:")
        wait = WebDriverWait(self.driver, 10)
        self.driver.get("https://google.com/ncr")
        self.driver.find_element(By.NAME,"q").send_keys("cheese" + Keys.RETURN)
        first_result = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Show more']")))
        
        print("  Verifying google results page includes a \"Show More\" element")
        self.assertEqual('Show more', first_result.get_attribute("textContent"))

    #Scneario 1: Verify Bookyte's Seller Profile address is "2800 Pringle Rd SE Suite 100"
    def test_bookbyte_amazon_address(self):
        expected = "2800 Pringle Rd SE Suite 100"
        
        print() #prettify output
        print("Scenario 1:")
        self.driver.get("https://www.amazon.com/sp?seller=A2N51X1QYGFUPK")
        wait = WebDriverWait(self.driver, 10)
        addressXpath = "//div[@id='seller-profile-container']//span[.='Business Address:']/following-sibling::ul/li[position()=1]/span"
        wait.until(EC.presence_of_element_located((By.XPATH, addressXpath)))
        addressSpan = self.driver.find_element(By.XPATH, addressXpath)
        
        actual = addressSpan.get_attribute('textContent')

        print("  Verifying Seller Profile address: expected (" + expected + ") vs. actual (" + actual + ")")
        self.assertEqual(expected, actual)

    #Scenario 2: Verify Result page after using Bookbyte's advanced search page to find the keyword "college"
    def test_bookbyte_advanced_search_functionality(self):
        keywordSearchString = "college"
        expectedPageTitle = "You searched for the keyword: " + keywordSearchString
        
        print() #prettify output
        print("Scenario 2:")
        self.driver.get("https://www.bookbyte.com/advancedsearch.aspx")
        wait = WebDriverWait(self.driver, 10)

        keywordXpath = "//input[@type='text' and contains(@id, 'tbKeywords')]"
        wait.until(EC.presence_of_element_located((By.XPATH, keywordXpath)))
        keywordInput = self.driver.find_element(By.XPATH, keywordXpath)
        keywordInput.clear()
        keywordInput.send_keys(keywordSearchString)

        searchButtonXpath = "//input[@type='image' and contains(@name, 'Search')]"
        wait.until(EC.presence_of_element_located((By.XPATH, searchButtonXpath)))
        self.driver.find_element(By.XPATH, searchButtonXpath).send_keys(Keys.ENTER)

        wait.until(EC.url_to_be("https://www.bookbyte.com/searchresults.aspx?type=BOOKS&kwd=" + keywordSearchString))
        print("  Verifying page title includes the search string (" + keywordSearchString + ")")
        self.assertEqual(self.driver.title, expectedPageTitle)
        
        resultBreadcrumbXpath = "//span[contains(@property, 'title')]"
        wait.until(EC.presence_of_element_located((By.XPATH, resultBreadcrumbXpath)))
        breadcrumb = self.driver.find_element(By.XPATH, resultBreadcrumbXpath)
        print("  Verifying page breadcrumb includes the search string (" + keywordSearchString + ")")
        self.assertEqual(breadcrumb.get_attribute("textContent"), keywordSearchString)
        
        resultCountStringKeywordXpath = "//span[@class='fntSubtitle']/i/span"
        wait.until(EC.presence_of_element_located((By.XPATH, resultBreadcrumbXpath)))
        searchStringPart = self.driver.find_element(By.XPATH, resultCountStringKeywordXpath)
        print("  Verifying total result statement includes the search string (" + keywordSearchString + ")")
        self.assertEqual(searchStringPart.get_attribute("textContent"), keywordSearchString)

    #Scenario 3: Verify Google Books API - Request book ISBN "0131103628" authors "Brian W. Kernighan" & "Dennis M. Ritchie"
    def test_google_book_api_book_search(self):
        targetISBN = "0131103628"
        bookTitle = "The C Programming Language"
        expectedAuthors = ["Brian W. Kernighan", "Dennis M. Ritchie"]
        
        print() #prettify output
        print("Scenario 3:")
        print("  Searching Google Books API for book information on ISBN " + targetISBN + ", titled " + bookTitle)
        print("  Verifying authors are attributed correctly, expecting " + ", ".join(expectedAuthors))
        
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
