import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import webdriver_manager
from webdriver_manager.chrome import ChromeDriverManager
import time
import re # for regular expression

# Setup WebDriver
options = Options()
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Navigate to the page
driver.get("https://www.indeed.com/")


# Enter location or "remote"
keywords_loc = driver.find_element(By.XPATH, '//*[@id="text-input-where"]')
keywords_loc.clear()  # Remove words already in keyword
keywords_loc.send_keys("San Francisco")
keywords_loc.submit()


# Wait for the keywords input field to be visible and interactable
keywords = driver.find_element(By.XPATH, '//*[@id="text-input-what"]')
keywords.send_keys("")
keywords.submit()




jobs_data = []  # List to store job data

#while true continues until there's no job matches on a given the page
while True: 
        #on a page, get the current jobs there 
    jobs = driver.find_elements(By.CSS_SELECTOR, ".job_seen_beacon")
        
        #for every job on the page
    for job in jobs:
            #get the title
        title = job.find_element(By.CSS_SELECTOR, "a > span").get_attribute('title')
            #get the company
        company_name = job.find_element(By.CSS_SELECTOR, ".css-92r8pb.eu4oa1w0").text
            #get the location
        company_location = job.find_element(By.CSS_SELECTOR, ".css-1p0sjhy.eu4oa1w0").text
        link = job.find_element(By.CSS_SELECTOR, "a").get_attribute('href')

        # Navigate to job detail page in a new tab
        driver.execute_script("window.open('');")  # Open new tab
        driver.switch_to.window(driver.window_handles[1])  # Switch to the new tab
        driver.get(link)  # Open job link
        
        try:
            salary = driver.find_element(By.XPATH,'//*[@id="salaryInfoAndJobType"]').text
        except NoSuchElementException:
            salary = "-99"
        # Check if the text contains both numbers and characters
        if salary != "-99" and re.search(r'\d', salary) and re.search(r'[a-zA-Z]', salary):
            # Extracted salary information meets the criteria
            pass  # No need to update, as salary already meets the criteria
        else:
            # Set a default value if the salary information doesn't meet the criteria
            salary = "-99"
        job_description = driver.find_element(By.CSS_SELECTOR,'#jobDescriptionText').text

        # Add entry as a row in the dataset
        job_entry = {
            "Title": title,
            "Company": company_name,
            "Location": company_location,
            "Salary": salary,
            "Link": link,
            "Description": job_description
        }
        
        #append each row (for all the jobs on the page (so usually 15 at a time)
        jobs_data.append(job_entry)

        driver.close()  # Close the current tab
        driver.switch_to.window(driver.window_handles[0])  # Switch back to the main tab


        # Attempt to go to the next page (try
    try:
        #if there's a "next page", click next, if sucessful, the "While true" starts again
        next_page = driver.find_element(By.CSS_SELECTOR, "a[data-testid='pagination-page-next']")
        next_page.click()
        # If there's no next page, exit the loop (same for only one-page job searches)
    except NoSuchElementException:
        break  
    
#close the browser when done
driver.close()


#save to dataset

jd = pd.DataFrame(jobs_data)


jd.to_csv("jobs_data.csv", index=False)