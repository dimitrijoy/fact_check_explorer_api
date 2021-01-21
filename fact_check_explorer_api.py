from constants import CLAIMANT_END, CLAIMANT_START, TIME_LIMIT
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# driver options
options = webdriver.ChromeOptions()
options.add_argument("--headless")

# gets top result of query, including claimant, claim, rating, and reference
def fetch(query):
    query = prepare(query)
    driver = webdriver.Chrome(options=options)
    driver.get(f"https://toolbox.google.com/factcheck/explorer/search/{query};hl=en")
    try:
        claimant = WebDriverWait(driver, TIME_LIMIT).until(
            EC.presence_of_element_located((By.XPATH, ".//div[@title='Claimant']"))
        )
        claim = WebDriverWait(driver, TIME_LIMIT).until(
            EC.presence_of_element_located((By.XPATH, ".//div[@title='Claim text']"))
        )
        rating = WebDriverWait(driver, TIME_LIMIT).until(
            EC.presence_of_element_located((By.XPATH, ".//span[@title='Publisher rating']"))
        )
        source = WebDriverWait(driver, TIME_LIMIT).until(
            EC.presence_of_element_located((By.XPATH, ".//span[@title='Publisher name']"))
        )
        reference = WebDriverWait(driver, TIME_LIMIT).until(
            EC.presence_of_element_located((By.XPATH, ".//a[@title='View article in a new window']"))
        )
        return package(claimant.text[CLAIMANT_START:CLAIMANT_END], claim.text, rating.text, source.text, reference.get_attribute("href"))
    except TimeoutException:
        pass
    finally:
        driver.quit()
    return None

# gets all results of query, including claimant, claim, rating, and reference for each
def fetchall(query):
    query = prepare(query)
    driver = webdriver.Chrome(options=options)
    driver.get(f"https://toolbox.google.com/factcheck/explorer/search/{query};hl=en")
    try:
        claimants = WebDriverWait(driver, TIME_LIMIT).until(
            EC.presence_of_all_elements_located((By.XPATH, ".//div[@title='Claimant']"))
        )
        claims = WebDriverWait(driver, TIME_LIMIT).until(
            EC.presence_of_all_elements_located((By.XPATH, ".//div[@title='Claim text']"))
        )
        ratings = WebDriverWait(driver, TIME_LIMIT).until(
            EC.presence_of_all_elements_located((By.XPATH, ".//span[@title='Publisher rating']"))
        )
        sources = WebDriverWait(driver, TIME_LIMIT).until(
            EC.presence_of_all_elements_located((By.XPATH, ".//span[@title='Publisher name']"))
        )
        references = WebDriverWait(driver, TIME_LIMIT).until(
            EC.presence_of_all_elements_located((By.XPATH, ".//a[@title='View article in a new window']"))
        )
        res = []
        for i in range(len(claimants)):
            res.append(package(claimants[i].text[CLAIMANT_START:CLAIMANT_END], claims[i].text, ratings[i].text, sources[i].text, references[i].get_attribute("href")))
        return res
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