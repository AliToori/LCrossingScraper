#!/usr/bin/env python3
"""
    *******************************************************************************************
    AmazonBot.
    Author: Ali Toori, Python Developer [Web-Automation Bot Developer | Web-Scraper Developer]
    Profiles:
        Upwork: https://www.upwork.com/freelancers/~011f08f1c849755c46
        Fiver: https://www.fiverr.com/alitoori
    *******************************************************************************************
"""
import os
import time
import random
import ntplib
import datetime
import pyfiglet
import pandas as pd
import logging.config
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support import expected_conditions as EC

logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    'formatters': {
        'colored': {
            '()': 'colorlog.ColoredFormatter',  # colored output
            # --> %(log_color)s is very important, that's what colors the line
            'format': '[%(asctime)s] %(log_color)s%(message)s'
        },
    },
    "handlers": {
        "console": {
            "class": "colorlog.StreamHandler",
            "level": "INFO",
            "formatter": "colored",
            "stream": "ext://sys.stdout"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": [
            "console"
        ]
    }
})

LOGGER = logging.getLogger()
GOOGLE_HOME_URL = "https://www.google.com/"


class LCrossing:

    def __init__(self):
        self.first_time = True
        self.PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

    # Get random user-agent
    def get_random_user_agent(self):
        file_path = os.path.join(self.PROJECT_ROOT, 'LCrossingRes/user_agents.txt')
        user_agents_list = []
        with open(file_path) as f:
            content = f.readlines()
        user_agents_list = [x.strip() for x in content]
        return random.choice(user_agents_list)

    # Login to the website for smooth processing
    def get_driver(self):
        # For absolute chromedriver path
        PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
        DRIVER_BIN = os.path.join(PROJECT_ROOT, "bin/chromedriver_win32.exe")
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_argument(F'--user-agent={self.get_random_user_agent()}')
        # options.add_argument('--headless')
        # driver = webdriver.Chrome(executable_path=DRIVER_BIN, options=options)
        driver = webdriver.Chrome(executable_path=DRIVER_BIN, options=options)
        return driver

    def get_data(self):
        driver = self.get_driver()
        print('Scraping LawCrossing resume database')
        file_path_keyword = os.path.join(self.PROJECT_ROOT, 'LCrossingRes/KeyWord.txt')
        file_path_title = os.path.join(self.PROJECT_ROOT, 'LCrossingRes/JobTitle.txt')
        file_path_country = os.path.join(self.PROJECT_ROOT, 'LCrossingRes/Country.txt')
        file_path_city = os.path.join(self.PROJECT_ROOT, 'LCrossingRes/City.txt')
        with open(file_path_keyword) as f:
            content = f.readlines()
        keyword = [x.strip() for x in content[0].split(':')][0]
        LOGGER.info("Keywords: " + str(keyword))
        # Get Job title from input file
        with open(file_path_title) as f:
            content = f.readlines()
        title = [x.strip() for x in content[0].split(':')][0]
        LOGGER.info("Job Titles: " + str(title))
        title = title.replace(" ", "+")
        # Get Country name from input file
        with open(file_path_country) as f:
            content = f.readlines()
        country_name = [x.strip() for x in content[0].split(':')][0]
        LOGGER.info("Country: " + str(country_name))
        country = country_name.replace(" ", "+")
        # Get City name from input file
        with open(file_path_city) as f:
            content = f.readlines()
        city_name = [x.strip() for x in content[0].split(':')][0]
        LOGGER.info("City: " + str(city_name))
        url_keyword = 'https://www.lawcrossing.com/employers/resume-search.php?&frmtp=otherlegal&kw='
        url_title = '&text=&jt='
        url_country_a = '&text=&ind=&text=&skl=&text=&frm=&mi_ex=&ma_ex=&text=&dgr=&text=&uni=&fr_grdy=&to_grdy=&rg_sel=single&co='
        url_country_b = '&text=&loc=&radius=50&mco='
        url_page = '&text=&mloc=&rsu=&scrtcl=&asoc=&cert=&lang=&page='
        # today = datetime.datetime.today().strftime('a%m-a%d-%y').replace('a0', 'a').replace('a', '')
        page_first = '1'
        file_lcrossing_temp = os.path.join(self.PROJECT_ROOT, 'LCrossingRes/LCrossingTemp.csv')
        df_lcrossing_temp = pd.read_csv(file_lcrossing_temp, index_col=None)
        if len(df_lcrossing_temp) <= 3:
            url_final = url_keyword + keyword + url_title + title + url_country_a + country + url_country_b + country + url_page + page_first
            LOGGER.info("Requesting page: " + str(url_final))
            driver.get(url_final)
            # Wait until the home page appears
            try:
                LOGGER.info("Waiting for advanced search to become visible:" + ' Keyword: ' + str(keyword))
                wait_until_visible(driver, xpath='//*[@id="ui-id-2"]')
                driver.find_element_by_xpath('//*[@id="ui-id-2"]').click()
                driver.find_element_by_tag_name('html').send_keys(Keys.SPACE)
                driver.find_element_by_tag_name('html').send_keys(Keys.SPACE)
                LOGGER.info("Waiting for location input to become visible")
                wait_until_visible(driver, xpath='//*[@id="token-input-location"]')
                loc_input = driver.find_element_by_xpath('//*[@id="token-input-location"]')
                loc_input.send_keys(city_name)
                LOGGER.info("Waiting for 12 seconds for the city to become visible")
                sleep(12)
                loc_input.send_keys(Keys.ENTER)
                # Press Enter key and then click search button
                # driver.find_element_by_tag_name('html').send_keys(Keys.ENTER)
                driver.find_element_by_xpath('//*[@id="advanceSubmit"]').click()
                LOGGER.info("Waiting for the page to become visible")
                wait_until_visible(driver, xpath='//*[@id="header"]')
            except:
                pass
            # Get page URL and rearrange it
            LOGGER.info("Grabbing page URL")
            url_final = str(driver.current_url).replace('page=1', '') + '&page='
            LOGGER.info("Requesting page: " + str(url_final + page_first))
            driver.get(url_final + page_first)
            LOGGER.info("Waiting for the page to become visible")
            wait_until_visible(driver, xpath='//*[@id="header"]')
            driver.find_element_by_tag_name('html').send_keys(Keys.SPACE)
            LOGGER.info("Waiting for the page count to become visible")
            wait_until_visible(driver, xpath='//*[@id="page-wrap"]/div[2]/div[1]/span/strong[2]')
            pages = str(driver.find_element_by_xpath('//*[@id="page-wrap"]/div[2]/div[1]/span/strong[2]').text).strip()
            LOGGER.info("Pages found:" + pages)
            pages = int(pages)
            for page in range(2, pages):
                LOGGER.info("Waiting for the page to become visible:" + ' Keyword ' + str(keyword) + ' Page No. ' + str(page))
                wait_until_visible(driver, xpath='//*[@id="header"]')
                # LOGGER.info("Scrolling to the end of the page:" + ' Keyword ' + keyword + ' Page No. ' + str(page))
                driver.find_element_by_tag_name('html').send_keys(Keys.END)
                # LOGGER.info("Waiting for the items to become visible:" + ' Keyword ' + keyword + ' Page No. ' + str(page))
                # If page is empty, break the page looping
                try:
                    wait_until_visible(driver, class_name='jobTitleWrap', duration=20)
                except:
                    item_dict = {"NAME": ['name'], "FIRM": ['firm_name'], "JOB TITLE": ['job_title'],
                                 "KEYWORD": [keyword], "COMPLETE": ["Yes"]}
                    df = pd.DataFrame(item_dict)
                    # if file does not exist write headers
                    if not os.path.isfile(file_lcrossing_temp) or os.path.getsize(file_lcrossing_temp) == 0:
                        df.to_csv(file_lcrossing_temp, index=False)
                    else:  # else if exists so append without writing the header
                        df.to_csv(file_lcrossing_temp, mode='a', header=False, index=False)
                    break
                for item in driver.find_elements_by_class_name('jobTitleWrap'):
                    name = item.find_element_by_tag_name('h3').text
                    name = str(name).strip().replace('"', '').replace(',', '').replace('', '')
                    firm_name = item.find_elements_by_tag_name('p')[2].text
                    firm_name = str(firm_name).strip()[6:].strip().replace('"', '').replace(',', '').replace('', '')
                    job_title = item.find_elements_by_tag_name('p')[3].text
                    job_title = str(job_title).strip()[11:].strip().replace('"', '').replace(',', '').replace('', '')
                    item_dict = {"NAME": [name], "FIRM": [firm_name], "JOB TITLE": [job_title], "KEYWORD": [keyword],
                                 "COMPLETE": ["No"]}
                    if page == pages:
                        item_dict = {"NAME": [name], "FIRM": [firm_name], "JOB TITLE": [job_title],
                                     "KEYWORD": [keyword], "COMPLETE": ["Yes"]}
                    LOGGER.info(name + "|" + str(firm_name) + ' Keyword ' + str(keyword) + ' Page No. ' + str(page))
                    df = pd.DataFrame(item_dict)
                    # if file does not exist write headers
                    if not os.path.isfile(file_lcrossing_temp) or os.path.getsize(file_lcrossing_temp) == 0:
                        df.to_csv(file_lcrossing_temp, index=False)
                    else:  # else if exists so append without writing the header
                        df.to_csv(file_lcrossing_temp, mode='a', header=False, index=False)
                LOGGER.info("Waiting for 3 seconds")
                sleep(3)
                url_final = url_final + str(page)
                LOGGER.info("Requesting page: " + str(url_final))
                driver.get(url_final)
        else:
            LOGGER.info("Scraping LinkedIn for resumes keyword: " + str(keyword))
            LOGGER.info("Waiting for Google to become visible: " + str(keyword))
            driver.get(GOOGLE_HOME_URL)
            search_url = 'https://www.google.com/search?q='
            file_lcrossing = os.path.join(self.PROJECT_ROOT,
                                          'LCrossingRes/LCrossing_' + str(title) + '_' + str(keyword) + '.csv')
            df_lcrossing_temp = pd.read_csv(file_lcrossing_temp, index_col=None)
            for item in df_lcrossing_temp.iloc:
                LOGGER.info("Waiting for 10 seconds")
                sleep(10)
                search_item = str(item["NAME"]) + " " + str(item["FIRM"]) + " LinkedIn"
                LOGGER.info("Searching for: " + search_item)
                search_item = search_item.replace(' ', '+')
                final_url = search_url + search_item
                driver.get(final_url)
                LOGGER.info("Waiting for Google to become visible:")
                wait_until_visible(driver, xpath='//*[@id="logo"]')
                LOGGER.info("Waiting for Google search results to become visible:")
                wait_until_visible(driver, xpath='//*[@id="rso"]')
                linkedin_profile = driver.find_element_by_xpath('//*[@id="rso"]').find_elements_by_tag_name('div')[
                    0].find_element_by_tag_name('a').get_attribute('href')
                df = {"NAME": [item["NAME"]], "FIRM": [item["FIRM"]], "JOB TITLE": [item["JOB TITLE"]],
                      "LinkedIn URL": [linkedin_profile]}
                LOGGER.info(str(item["NAME"]) + "|" + str(item["FIRM"]) + " LinkedIn URL: " + str(linkedin_profile))
                df = pd.DataFrame(df)
                # if file does not exist write header
                if not os.path.isfile(file_lcrossing) or os.path.getsize(file_lcrossing) == 0:
                    df.to_csv(file_lcrossing, index=False)
                else:  # else if exists so append without writing the header
                    df.to_csv(file_lcrossing, mode='a', header=False, index=False)
        self.finish(driver)

    def finish(self, driver):
        try:
            driver.close()
            driver.quit()
        except WebDriverException as exc:
            print('Problem occurred while closing the WebDriver instance ...', exc.args)


def wait_until_clickable(driver, xpath=None, element_id=None, name=None, class_name=None, css_selector=None,
                         duration=10000, frequency=0.01):
    if xpath:
        WebDriverWait(driver, duration, frequency).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    elif element_id:
        WebDriverWait(driver, duration, frequency).until(EC.element_to_be_clickable((By.ID, element_id)))
    elif name:
        WebDriverWait(driver, duration, frequency).until(EC.element_to_be_clickable((By.NAME, name)))
    elif class_name:
        WebDriverWait(driver, duration, frequency).until(EC.element_to_be_clickable((By.CLASS_NAME, class_name)))
    elif css_selector:
        WebDriverWait(driver, duration, frequency).until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))


def wait_until_visible(driver, xpath=None, element_id=None, name=None, class_name=None, css_selector=None,
                       duration=10000, frequency=0.01):
    if xpath:
        WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.XPATH, xpath)))
    elif element_id:
        WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.ID, element_id)))
    elif name:
        WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.NAME, name)))
    elif class_name:
        WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.CLASS_NAME, class_name)))
    elif css_selector:
        WebDriverWait(driver, duration, frequency).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector)))


def main():
    l_crossing = LCrossing()
    # Getting Day before Yesterday
    # day_before_yesterday = (datetime.datetime.now() - datetime.timedelta(2)).strftime('%m/%d/%Y')
    # while True:
    l_crossing.get_data()
    # except WebDriverException as exc:
    #     print('Exception in WebDriver:', exc.msg)


# Trial version logic
def trial(trial_date):
    ntp_client = ntplib.NTPClient()
    response = ntp_client.request('pool.ntp.org')
    local_time = time.localtime(response.ref_time)
    current_date = time.strftime('%Y-%m-%d %H:%M:%S', local_time)
    current_date = datetime.datetime.strptime(current_date, '%Y-%m-%d %H:%M:%S')
    return trial_date > current_date


if __name__ == '__main__':
    trial_date = datetime.datetime.strptime('2020-11-12 23:59:59', '%Y-%m-%d %H:%M:%S')
    # Print ASCII Art
    print('************************************************************************\n')
    pyfiglet.print_figlet('____________               LCrossingBot ____________\n', colors='RED')
    print('Author: Ali Toori, Python Developer [Web-Automation Bot Developer]\n'
          'Profiles:\n\tUpwork: https://www.upwork.com/freelancers/~011f08f1c849755c46\n\t'
          'Fiver: https://www.fiverr.com/alitoori\n************************************************************************')
    # Trial version logic
    if trial(trial_date):
        # print("Your trial will end on: ",
        #       str(trial_date) + ". To get full version, please contact fiverr.com/AliToori !")
        main()
    else:
        pass
        # print("Your trial has been expired, To get full version, please contact fiverr.com/AliToori !")
