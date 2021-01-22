# dependencies
from constants import CLAIMANT_END, CLAIMANT_START, TIME_LIMIT
from fuzzywuzzy import fuzz
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# driver options
options = webdriver.ChromeOptions()
options.add_argument("--headless")

# gets top result of query, including claimant, claim, rating, and reference
def fetch(query, smart=False):
    driver = webdriver.Chrome(options=options)
    driver.get(f"https://toolbox.google.com/factcheck/explorer/search/{prepare(query)};hl=en")
    try:
        if smart:
            cards = WebDriverWait(driver, TIME_LIMIT).until(
                EC.presence_of_all_elements_located((By.XPATH, ".//div[@class='fc-card-content']"))
            )
            fact_checks, index, max_set_ratio = [], 0, 0
            for i in range(len(cards)):
                card = cards[i]
                try: # claimant is sometimes missing
                    claimant = card.find_element_by_xpath(".//div[@title='Claimant']").text[CLAIMANT_START:CLAIMANT_END]
                except NoSuchElementException:
                    claimant = None
                claim = card.find_element_by_xpath(".//div[@title='Claim text']").text
                rating = card.find_element_by_xpath(".//span[@title='Publisher rating']").text
                source = card.find_element_by_xpath(".//span[@title='Publisher name']").text
                reference = card.find_element_by_xpath(".//a[@title='View article in a new window']").get_attribute("href")
                fact_checks.append(package(claimant, claim, rating, source, reference))
                set_ratio = fuzz.token_set_ratio(query, claim)
                if set_ratio > max_set_ratio:
                    index = i
                    max_set_ratio = set_ratio
            return fact_checks[index]
        else:
            card = WebDriverWait(driver, TIME_LIMIT).until(
                EC.presence_of_element_located((By.XPATH, ".//div[@class='fc-card-content']"))
            )
            try: # claimant is sometimes missing
                claimant = card.find_element_by_xpath(".//div[@title='Claimant']").text[CLAIMANT_START:CLAIMANT_END]
            except NoSuchElementException:
                claimant = None
            claim = card.find_element_by_xpath(".//div[@title='Claim text']").text
            rating = card.find_element_by_xpath(".//span[@title='Publisher rating']").text
            source = card.find_element_by_xpath(".//span[@title='Publisher name']").text
            reference = card.find_element_by_xpath(".//a[@title='View article in a new window']").get_attribute("href")
            return package(claimant, claim, rating, source, reference)
    except TimeoutException:
        pass
    finally:
        driver.quit()
    return None

# gets all results of query, including claimant, claim, rating, and reference for each
def fetchall(query):
    driver = webdriver.Chrome(options=options)
    driver.get(f"https://toolbox.google.com/factcheck/explorer/search/{prepare(query)};hl=en")
    try:
        cards = WebDriverWait(driver, TIME_LIMIT).until(
            EC.presence_of_all_elements_located((By.XPATH, ".//div[@class='fc-card-content']"))
        )
        fact_checks = []
        for card in cards:
            try: # claimant is sometimes missing
                claimant = card.find_element_by_xpath(".//div[@title='Claimant']").text[CLAIMANT_START:CLAIMANT_END]
            except NoSuchElementException:
                claimant = None
            claim = card.find_element_by_xpath(".//div[@title='Claim text']").text
            rating = card.find_element_by_xpath(".//span[@title='Publisher rating']").text
            source = card.find_element_by_xpath(".//span[@title='Publisher name']").text
            reference = card.find_element_by_xpath(".//a[@title='View article in a new window']").get_attribute("href")
            fact_checks.append(package(claimant, claim, rating, source, reference))
        return fact_checks
    except TimeoutException:
        pass
    finally:
        driver.quit()
    return None

# organizes data in dictionary
def package(claimant, claim, rating, source, reference):
    return {"claimant": claimant, "claim": claim, "rating": rating, "source": source, "reference": reference}

# query preprocessing
def prepare(query):
    return query.replace(" ", "%20")
