#=======================================================================================================================================
# Import libraries and dataframe 
#=======================================================================================================================================
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import time
import re
import pandas as pd
import os
import numpy as np

#=======================================================================================================================================
# Web scraping
#=======================================================================================================================================

driver = webdriver.Chrome(r'C:/Users/Guillermo/Desktop/ESTUDIOS/Data Science Bootcamp/Projects/Web scraping/5. Selenium/chromedriver_win32/chromedriver.exe')

# Get into the webpage search function
driver.get('https://www.glassdoor.com/Job/new-york-jobs-SRCH_IL.0,8_IC1132348.htm?radius=100')
time.sleep(3)
driver.maximize_window()
time.sleep(3)

# Prepare credentials to sing in Glassdoor
button = driver.find_element_by_xpath("//*[@id='TopNav']/nav/div[4]/a")
driver.execute_script("arguments[0].click();", button)
time.sleep(10)

username = driver.find_element_by_id("userEmail")
password = driver.find_element_by_id("userPassword")

username.send_keys("xxxxx")  # Private information 
password.send_keys("xxxxx")  # Private information

button = driver.find_element_by_xpath("//button[@type='submit']")
driver.execute_script("arguments[0].click();", button)
time.sleep(5)

# Change language to american english
driver.find_element_by_xpath("//*[@id='CountryUrlChooser']/option[23]").click()
time.sleep(5)
# Set search filters
driver.find_element_by_xpath("//*[@id='filter_radius']").click()
driver.find_element_by_xpath("//*[@id='PrimaryDropdown']/ul/li[7]").click()
time.sleep(5)

# Create variable with number of pages 
num_pages = driver.find_element_by_xpath('//*[@id="ResultsFooter"]/div[1]').text
num_pages = int(num_pages[-2:])

# Create list with links of all pages
result_urls = ["https://www.glassdoor.com/Job/new-york-jobs-SRCH_IL.0,8_IC1132348.htm?radius=100&p={}".format(x) for x in range(2, num_pages + 1)]
result_urls.append('https://www.glassdoor.com/Job/new-york-jobs-SRCH_IL.0,8_IC1132348.htm?radius=100')

# Create dictionary to collect the data
dic = {'job':[],'company':[], 'location':[], 'job_type':[], 'job_function':[], 'industry':[], 'size':[], 'employees':[], 'description':[], 'salaries':[]}

# Extract data
for url in result_urls:
    driver.get(url)
    time.sleep(3)
    # Create list with all links to the jobs in the page
    jobs_urls = [x.get_attribute('href') for x in driver.find_elements_by_xpath('//div[@class="d-flex flex-column pl-sm css-nq3w9f"]/a')]
    
    for job in jobs_urls:
        driver.get(job)
        time.sleep(3)
        
        # Job
        try:
            job = driver.find_element_by_xpath('//div[@class="css-17x2pwl e11nt52q6"]').text
        except:
            job = None    
        
        # Company
        try:
            company = driver.find_element_by_xpath('//div[@class="css-16nw49e e11nt52q1"]').text
        except:
            company = None

        # Location 
        try:
            location = driver.find_element_by_xpath('//div[@class="css-1v5elnn e11nt52q2"]').text
        except:
            location = None
        
        # Job type
        try:
            job_type = driver.find_element_by_xpath('//div[@class="css-1ieo3ql e18tf5om7"]/span[@class="css-sr4ps0 e18tf5om4"]').text
        except:
            job_type = None

        # Job function
        try:
            job_function = driver.find_element_by_xpath('//div[@class="css-1ieo3ql e18tf5om7"]/span[@class="css-o4d739 e18tf5om4"]').text
        except:
            job_function = None    
         
        # Industry
        try:
            industry = driver.find_element_by_xpath('(//div[@class="css-1ieo3ql e18tf5om7"]/span[@class="css-sr4ps0 e18tf5om4"])[2]').text
        except:
            industry = None

        # Size
        try:
            size = driver.find_element_by_xpath('(//div[@class="css-1ieo3ql e18tf5om7"]/span[@class="css-sr4ps0 e18tf5om4"])[3]').text
        except:
            size = None 

        
        # Description
        try:
            description = driver.find_element_by_xpath("//div[@class='desc css-58vpdc ecgq1xb4']").text
        except:
            description = None 
                    
        # Salaries
        try:
            button = driver.find_element_by_xpath('(//span[@class="link"])[3]')
            driver.execute_script("arguments[0].click();", button)
            time.sleep(3)
        except:
            pass    

        try:
            # get salaries published by the company
            all_spans = driver.find_elements_by_xpath("//div[@class='strong']")
            salaries = []
            for span in all_spans:
                salaries.append(span.text)
            # get jobs those salaries correspond to
            all_spans = driver.find_elements_by_xpath("//div[@class='jobTitle strong']")
            employees = []
            for span in all_spans:
                employees.append(span.text)    
        except:
            salaries = None
            employees = None   


        # Introduce data in the dictionary
        dic['job'].append(job)
        dic['company'].append(company)
        dic['location'].append(location)
        dic['job_type'].append(job_type)
        dic['job_function'].append(job_function)
        dic['industry'].append(industry)
        dic['size'].append(size)
        dic['employees'].append(employees)
        dic['description'].append(description)
        dic['salaries'].append(salaries)


#=======================================================================================================================================
# Save scraped data as a csv document
#=======================================================================================================================================

df = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in dic.items() ])) 

os.chdir('C:/Users/Guillermo/Desktop/ESTUDIOS/Data Science Bootcamp/Projects/Web scraping/Project')

df.to_csv('jobs.csv')


