"""
Upgrading the visa scheduler into a monetized app

Challenges:
1. Must be logged in a user's account to make requests
2. Potential blocks from the API
3. Users need to share their credentials
4. Does being a group processor make it easier to access the API?
5. Testing is challeging since the requests are all live

To solve:
1. Logic to prioritize users who have paid for the service OR run concurrent instances for each user (stop for one week on successful reschedules)?
2. Which user credentials to use for the requests (test if session cookie needs to be match the schedule owner)
3. The appointment request might not work 100% (tests needed)
4. Which DB technology to use
5. Run it as a lambda function

Solution:
1. Use a user's account to make requests
2. Run concurrent instances for each user
3. On successful reschedules, stop for one week

Learnings from latest test (see Latest test below to check the full log):
1. Checking if POST request status code 200 is not 100% accurate. Html page returned contains new schedule date, so that can be compared with the actual date that was requested
  1.1. HTML of the response already captured in response.html
2. These code lines are causing the value of msg to be an empty string (review and fix):
  2.1: msg = f"Rescheduled Successfully! {date} {time}" + f", ASC: {asc_date} {asc_time}" if NEED_ASC else ""
  2.2: msg = f"Reschedule Failed. {date} {time}" + f", ASC: {asc_date} {asc_time}" if NEED_ASC else ""
3. SendGrid requests are returning a Forbidden 403 response

Technical notes:
INFO:main - ---START--- : 2024-03-01 22:49:58.152577
INFO:login - Login start...
INFO:login - 	click bounce
INFO:do_login_action - 	input email
INFO:do_login_action - 	input pwd
INFO:do_login_action - 	click privacy
INFO:do_login_action - 	commit
INFO:do_login_action - 	login successful!
INFO:get_my_schedule_date - Getting my schedule date...
INFO:get_date - Getting dates...
INFO:print_dates - Available dates:
INFO:print_dates - 2024-04-01 	 business_day: True
INFO:print_dates - 2025-01-22 	 business_day: True
INFO:print_dates - 2025-01-27 	 business_day: True
INFO:print_dates - 2025-01-30 	 business_day: True
INFO:print_dates - 2025-02-03 	 business_day: True
INFO:get_available_date - Checking for an earlier date:
INFO:is_earlier - Is 2024-04-04 00:00:00 > 2024-04-01 00:00:00:	True
INFO:get_time - Got time successfully! 2024-04-01 07:45
INFO:main - New date: 2024-04-01 07:45
INFO:reschedule - Starting Reschedule (2024-04-01)
INFO:reschedule - 	multiple applicants
INFO:send_notification - Sending notification:
ERROR:send_notification - HTTP Error 400: Bad Request
INFO:send_notification - Sending notification: Earlier date found: 2024-04-01

Application stopped with a successful result after this
Continue with loop after success
My guess on the error: probably caused by a false successful response by the post request

Latest test:
INFO:main - ---START--- : 19/03/2024 21:58:45
INFO:login - Login start...
INFO:login - 	click bounce
INFO:do_login_action - 	input email
INFO:do_login_action - 	input pwd
INFO:do_login_action - 	click privacy
INFO:do_login_action - 	commit
INFO:do_login_action - 	login successful!
INFO:get_my_schedule_date - Getting my schedule date...
INFO:main - My schedule date: 2025-01-31
INFO:get_date - Getting dates...
INFO:print_dates - Available dates:
INFO:print_dates - 2025-02-03 	 business_day: True
INFO:print_dates - 2025-02-04 	 business_day: True
INFO:print_dates - 2025-02-05 	 business_day: True
INFO:print_dates - 2025-02-06 	 business_day: True
INFO:print_dates - 2025-02-10 	 business_day: True
INFO:get_available_date - Checking for an earlier and appropriate date:
INFO:get_time - Got time successfully! 2025-02-03 07:30
INFO:main - New date: 2025-02-03 07:30
INFO:reschedule - Starting Reschedule (2025-02-03)
INFO:reschedule - 	multiple applicants
INFO:reschedule - Reschedule response: 200
INFO:reschedule - Rescheduled Successfully! 2025-02-03 07:30
INFO:send_notification - Sending notification: Rescheduled Successfully! 2025-02-03 07:30
ERROR:send_notification - HTTP Error 403: Forbidden
INFO:send_notification - Sending notification: Earlier date found: 2025-02-03
ERROR:send_notification - HTTP Error 403: Forbidden

form action
	/en-ae/niv/schedule/38708221/appointment
inputs
	authenticity_token hidden
	confirmed_limit_message hidden
	use_consulate_appointment_capacity hidden
	appointments[consulate_appointment][facility_id]
	appointments[consulate_appointment][date]
	appointments[consulate_appointment][time]

data = {
    "authenticity_token": "BA98dXbmtGluf0FR/3PR08VDQWoY5jA6fef/kIssgB5rzQY615ai5Hzt79vc+KVlGx8lLiYgnhPFw50bGTuYVA==",
    "confirmed_limit_message": 1,
    "use_consulate_appointment_capacity": true,
    "appointments[consulate_appointment][facility_id]": 50,
    "appointments[consulate_appointment][date]": "2024-04-01",
    "appointments[consulate_appointment][time]": "07:45",
}
headers = {
    "User-Agent": "Mozilla Firefox",
    "Referer": "https://ais.usvisa-info.com/en-ae/niv/schedule/38708221/appointment",
    "Cookie": "_yatri_session=value"
}
r = requests.post("https://ais.usvisa-info.com/en-ae/niv/schedule/38708221/appointment", headers=headers, data=data)

curl -X POST \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0" \
  -H "Referer: https://ais.usvisa-info.com/en-ae/niv/schedule/56376709/appointment" \
  -H "Cookie: _yatri_session=lGXPPp58jacbMZRnXiFQvktDkA5xM3zVWtmQt4J27F4PmZeeISfgexxltBAj%2FdFCWU7bygoMoJoh5OsrWBwPdpnuwE6eBotRYA%2F%2F9%2FEN4gceC1n8JM0Ch0CbNYEH1N2B5tMVJv4MFC6UTRBUZbSMT7SN8Oyh%2BUztNoPCiZkcJe4INmmar7BQYdtk5G7iceCcb5Iy1VRGv3MRE%2FghBnhWqaLI1O6gZdpMbtUkB8xCE5om5f2ewGVWeliarG8fqUYOV4H0sq1bTbU7iMuKy82AIFzrqI5OlSOCuSy68U2P6cdJ71Qk%2Bkrm7hEVUMsznzjRjCc0iM1v5fcjqHiXIZtZXq%2F5Bl70eZImoD0CwWEp9I155qwhAwtzePXWXd6pRy8TScmr6%2F54UN1t%2FlyPlyezHQG6RDAKmrUlKGDjfq%2FwBkmJm2dOK2Kfh8%2B8OIDUR42riMmbqiyLDCjGmwgJdMoI2cv4Qu6rLbweezgoASqVsmcclhDuNin%2Fat6ln2Vw2FAV%2FuAyRAzqE8DRYwSMLxX4x%2BTRMg7SzCSGHPv9rekyBu8QvsePKnPJ0KfUDTgWOrbwv6CauY2RRpZF%2FvIbgEK5WFDCBVdejcgSlXkpDQionWb8gqxb57TtQ3SYTjiLxyL8Fq0VKIhLhDQ4rhaCmQg3hbGxMvgjK1wA8fVGFqWuCXJgyhJwo4xyt8hQB9cKZvRB62zQagFypPC5kbkU4z08nvq0Z9uyTWHQ9DIDLx3mufVqDZbE3ddmkl9c6X6OyaPPWPVsTowQGaYlqsKHmt33A9FhxWy8Wn9q1F3zEQXbMX9GGcYLMC3D9ALuQ9jLyVE90t4%3D--0juR23e67pKfSlXE--gIncvKJqA0l08D%2FOGVc2Dg%3D%3D" \
  -d "authenticity_token=I9KQvt6mtvQSqdPim%2BDL5s2Nb57TZuw9IvfkPvR2P%2BuzRtRDGMS6qoBQS9bIsgIfPG23tiQB8ST1pdVFcRt0Sw%3D%3D" \
  -d "confirmed_limit_message=1" \
  -d "use_consulate_appointment_capacity=true" \
  -d "appointments[consulate_appointment][facility_id]=50" \
  -d "appointments[consulate_appointment][date]=2025-01-14" \
  -d "appointments[consulate_appointment][time]=08:00" \
  "https://ais.usvisa-info.com/en-ae/niv/schedule/56376709/appointment"

curl -X POST 'https://ais.usvisa-info.com/en-ae/niv/schedule/56376709/appointment' 
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0' 
  -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8' 
  -H 'Accept-Language: en-GB,en;q=0.5' 
  -H 'Accept-Encoding: gzip, deflate, br' 
  -H 'Referer: https://ais.usvisa-info.com/en-ae/niv/schedule/56376709/appointment?applicants%5B%5D=66318442&applicants%5B%5D=66318453&applicants%5B%5D=66318506&applicants%5B%5D=66318519&applicants%5B%5D=66318533&confirmed_limit_message=1&commit=Continue' 
  -H 'Content-Type: application/x-www-form-urlencoded' 
  -H 'Origin: https://ais.usvisa-info.com' 
  -H 'Connection: keep-alive' 
  -H 'Cookie: _yatri_session=2cdhn%2FmZvy9%2BfJrTlqYgrpalce1gK6gyCDc8SF1p2SWPVxFMP8EEWV60Pl%2F26UJgKE6%2BODYe1RyE8gkaQ%2BWZpbWmhPqY75Ve1ZstpUpDfdtUzitZtIlkO2rGGo6KCc4NESHz%2F9Mb%2BJNUcY9oS05%2BTn%2Fw5eiDrJ8Zq8H7JpFqDZnRyX72ppzB7b%2Bhdk3Te2ECbYgc4oI7z9Gh%2B%2F6%2BV2X7%2FweZwalgrRfU9zYmDf%2FHB3Znwet5vRu6tF%2FkHcLU%2BbbzTMjlZh0tbfJUypyLTzwWsBSMm%2FC8MdbdJ2RfQb7ZRzbwANkOVlcQzA9omKpteczifSGP6uOWriFOcZsz5Q8andYx61Aa4E4KTm8YoDWYVkwZklRr3vujIblsGnbsSSUDBv15TbBpGkGu5STcllIZMi6dtwlFKMjCiE3ohnnwilX2Z6dRLLvlKxCmrfkrJi7X8g5Qy1XcqJoqJcbRsIxPTjWutnyuEmc7vm%2BPDk9FXX%2B3UT60NvmgZGGW6QJk%2FKci9QjbP9139aS0HVrZIWho5vPgaBFHkD0rxHLpqwBsgQcUeqgQlMvo47MspN0EpRKPq1WsFqQKkAoultE9CHlFGLGtYE56azV2I57jePnVX%2FATd6VAImPdBIHSmceoJiKG2GruP0QTIWFdrb5sI7yiDzvIWT1HgCh2xBiQBDJWjY%2BCZzNUoqCQu1wYWZrUAKzIGKGjeMmYGEEKow0ThlH16fS8v7CUMllYd2AvxwruSntWzhLN95b%2F8aWSUJljP%2B%2FsKUhrpwoCd%2Bko5N8uvIICkwB8bzpgCryMx1S4xfPX2mQ9u2mJH74JohTaPaIszw%3D%3D--d0AJcfkPVoJ%2B3NoT--ye8pl9gG%2Fe4ojRh3DyKFtg%3D%3D' 
  -H 'Upgrade-Insecure-Requests: 1' 
  -H 'Sec-Fetch-Dest: document' 
  -H 'Sec-Fetch-Mode: navigate' 
  -H 'Sec-Fetch-Site: same-origin' 
  -H 'Sec-Fetch-User: ?1' 
  -H 'Pragma: no-cache' 
  -H 'Cache-Control: no-cache' --data-raw 'authenticity_token=lw585UVIir2lt9sbpbtwqOPo%2Fcnck53E9IWLkZr4Oqs5PVeJ0rWlrL58ImDzckbbgUbKi7IgeffhMzpjo290mA%3D%3D&confirmed_limit_message=1&use_consulate_appointment_capacity=true&appointments%5Bconsulate_appointment%5D%5Bfacility_id%5D=50&appointments%5Bconsulate_appointment%5D%5Bdate%5D=2025-01-14&appointments%5Bconsulate_appointment%5D%5Btime%5D=08%3A00'

Response for invalid dates:
<html><body>You are being <a href="https://ais.usvisa-info.com/en-ae/niv/schedule/56376709/appointment/instructions">redirected</a>.</body></html>
""" 

# -*- coding: utf8 -*-
import configparser
import logging
import random
import re
import sys
import time as tm
from datetime import datetime, timedelta
from enum import Enum
from tempfile import mkdtemp

import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from webdriver_manager.chrome import ChromeDriverManager

from utils import Result

console = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(levelname)s:%(funcName)s - %(message)s')
console.setFormatter(formatter)
logger = logging.getLogger("Visa_Logger")
logger.addHandler(console)
logger.setLevel(logging.DEBUG)

config = configparser.ConfigParser()
config.read('config.ini')

USERNAME = config['USVISA']['USERNAME']
PASSWORD = config['USVISA']['PASSWORD']
SCHEDULE_ID = config['USVISA']['SCHEDULE_ID']
COUNTRY_CODE = config['USVISA']['COUNTRY_CODE']
FACILITY_ID = config['USVISA']['FACILITY_ID']
ASC_ID = config['USVISA']['ASC_ID']
NEED_ASC = config['USVISA'].getboolean('NEED_ASC')

SENDGRID_API_KEY = config['SENDGRID']['SENDGRID_API_KEY']
PRIMARY_EMAIL_RECIPIENT = config['SENDGRID']['PRIMARY_EMAIL_RECIPIENT']
PUSH_TOKEN = config['PUSHOVER']['PUSH_TOKEN']
PUSH_USER = config['PUSHOVER']['PUSH_USER']

USE = config['CHROMEDRIVER']['USE']

REGEX_CONTINUE = "//a[contains(text(),'Continue')]"

STEP_TIME = 0.5  # time between steps (interactions with forms): 0.5 seconds

DATE_URL = f"https://ais.usvisa-info.com/{COUNTRY_CODE}/niv/schedule/{SCHEDULE_ID}/appointment/days/{FACILITY_ID}.json?appointments[expedite]=false"
TIME_URL = f"https://ais.usvisa-info.com/{COUNTRY_CODE}/niv/schedule/{SCHEDULE_ID}/appointment/times/{FACILITY_ID}.json?date={{date}}&appointments[expedite]=false"
APPOINTMENT_URL = f"https://ais.usvisa-info.com/{COUNTRY_CODE}/niv/schedule/{SCHEDULE_ID}/appointment"
DATE_URL_ASC = f"https://ais.usvisa-info.com/{COUNTRY_CODE}/niv/schedule/{SCHEDULE_ID}/appointment/days/{ASC_ID}.json?&consulate_id={FACILITY_ID}&consulate_date={{date}}&consulate_time={{time}}&appointments[expedite]=false"
TIME_URL_ASC = f"https://ais.usvisa-info.com/{COUNTRY_CODE}/niv/schedule/{SCHEDULE_ID}/appointment/times/{ASC_ID}.json?date={{date_asc}}&consulate_id={FACILITY_ID}&consulate_date={{date}}&consulate_time={{time}}&appointments[expedite]=false"

class Use(Enum):
    AWS = "AWS"
    LOCAL = "LOCAL"

class VisaScheduler:
    def __init__(self):
        self.my_schedule_date = None

    def get_header(self):
        return {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": self.driver.execute_script("return navigator.userAgent;"),
            "Referer": APPOINTMENT_URL,
            "Cookie": "_yatri_session=" + self.driver.get_cookie("_yatri_session")["value"]
        }

    def get_my_schedule_date(self):
        logger.info("Getting my schedule date...")
        element = self.driver.find_element(By.XPATH,
                                           '//a[contains(@href, "%s")]/ancestor::div[contains(@class, "application")]' % SCHEDULE_ID)

        appointment = element.find_element(By.CLASS_NAME, 'consular-appt').text
        regex = r".+: (.+,.+),.+"
        date = re.search(regex, appointment).group(1)
        self.my_schedule_date = datetime.strptime(date, "%d %B, %Y").strftime("%Y-%m-%d")

    def login(self):
        # Bypass reCAPTCHA
        self.driver.get(f"https://ais.usvisa-info.com/{COUNTRY_CODE}/niv")
        tm.sleep(STEP_TIME)
        a = self.driver.find_element(By.XPATH, '//a[@class="down-arrow bounce"]')
        a.click()
        tm.sleep(STEP_TIME)

        logger.info("Login start...")
        href = self.driver.find_element(By.XPATH, '//*[@id="main"]/div[2]/div[3]/div[2]/div[1]/div/a')
        href.click()
        tm.sleep(STEP_TIME)
        Wait(self.driver, 60).until(EC.presence_of_element_located((By.NAME, "commit")))

        logger.info("\tclick bounce")
        a = self.driver.find_element(By.XPATH, '//a[@class="down-arrow bounce"]')
        a.click()
        tm.sleep(STEP_TIME)

        self.do_login_action()

    def do_login_action(self):
        logger.info("\tinput email")
        user = self.driver.find_element(By.ID, 'user_email')
        user.send_keys(USERNAME)
        tm.sleep(random.randint(1, 3))

        logger.info("\tinput pwd")
        pw = self.driver.find_element(By.ID, 'user_password')
        pw.send_keys(PASSWORD)
        tm.sleep(random.randint(1, 3))

        logger.info("\tclick privacy")
        box = self.driver.find_element(By.CLASS_NAME, 'icheckbox')
        box.click()
        tm.sleep(random.randint(1, 3))

        logger.info("\tcommit")
        btn = self.driver.find_element(By.NAME, 'commit')
        btn.click()
        tm.sleep(random.randint(1, 3))

        Wait(self.driver, 60).until(
            EC.presence_of_element_located((By.XPATH, REGEX_CONTINUE)))
        logger.info("\tlogin successful!")

    def get_date(self):
        if not self.is_logged_in():
            self.login()
            return self.get_date()
        else:
            logger.info("Getting dates...")
            r = requests.get(DATE_URL, headers=self.get_header())
            if r.status_code == 401:
                print("Unauthorized. Logging back in...")
                self.login()
                return self.get_date()
            
            date = r.json()
            return date

    def get_time(self, date):
        time_url = TIME_URL.format(date=date)
        r = requests.get(time_url, headers=self.get_header())
        data = r.json()
        times = data.get("available_times")[::-1]
        for t in times:
            hour, minute = t.split(":")
            if self.MY_CONDITION_TIME(hour, minute):
                logger.info(f"Got time successfully! {date} {t}")
                return t

    def reschedule(self, date, time, asc_date=None, asc_time=None):
        logger.info(f"Starting Reschedule ({date})")

        self.driver.get(APPOINTMENT_URL)

        tm.sleep(STEP_TIME)
        try:
            btn = self.driver.find_element(By.XPATH, '//*[@id="main"]/div[3]/form/div[2]/div/input')

            logger.info("\tmultiple applicants")
            btn.click()
        except NoSuchElementException:
            logger.info("\tsingle applicant")

        data = {
            "authenticity_token": self.driver.find_element(by=By.NAME, value='authenticity_token').get_attribute(
                'value'),
            "confirmed_limit_message": self.driver.find_element(by=By.NAME,
                                                                value='confirmed_limit_message').get_attribute(
                'value'),
            "use_consulate_appointment_capacity": self.driver.find_element(by=By.NAME,
                                                                           value='use_consulate_appointment_capacity').get_attribute(
                'value'),
            "appointments[consulate_appointment][facility_id]": FACILITY_ID,
            "appointments[consulate_appointment][date]": date,
            "appointments[consulate_appointment][time]": time,
        }

        if NEED_ASC:
            asc_data = {
                "appointments[asc_appointment][facility_id]": ASC_ID,
                "appointments[asc_appointment][date]": asc_date,
                "appointments[asc_appointment][time]": asc_time
            }
            data.update(asc_data)

        headers = {
            "User-Agent": self.driver.execute_script("return navigator.userAgent;"),
            "Referer": APPOINTMENT_URL,
            "Cookie": "_yatri_session=" + self.driver.get_cookie("_yatri_session")["value"]
        }

        r = requests.post(APPOINTMENT_URL, headers=headers, data=data)
        if r.status_code == 200:
            msg = f"Rescheduled Successfully! {date} {time}"
            logger.info(msg)
            self.send_notification(msg)
            return Result.SUCCESS
        else:
            msg = f"Reschedule Failed. {date} {time}"
            logger.error(msg)
            self.send_notification(msg)
            return Result.RETRY

    def asc_availability(self, date, time):
        logger.info("ASC Availability")

        def get_date():
            if not self.is_logged_in():
                self.login()
                return get_date()
            else:
                date_url_asc = DATE_URL_ASC.format(date=date, time=time)
                r = requests.get(date_url_asc, headers=self.get_header())
                return r.json()

        def get_available_date(dates):
            for d in dates:
                date = d.get('date')
                return date

        def get_time(date_asc):
            time_url = TIME_URL_ASC.format(date_asc=date_asc, date=date, time=time)
            r = requests.get(time_url, headers=self.get_header())
            data = r.json()
            available_times = data.get("available_times")[::-1]
            for t in available_times:
                logger.info(f"Got time successfully! {date_asc} {t}")
                return t

        dates = get_date()[:5]
        if not dates:
            return False, (None, None)

        available_date = get_available_date(dates)
        if not available_date:
            return True, (None, None)

        available_time = get_time(available_date)
        if not available_time:
            return True, (available_date, None)

        return True, (available_date, available_time)

    def is_logged_in(self):
        cookie = self.driver.get_cookie("_yatri_session")["value"]
        if len(cookie) <= 350:
            return False
        return True

    @staticmethod
    def get_driver():
        dr = None
        if USE == Use.LOCAL.value:
            chrome_options = webdriver.ChromeOptions()
            # chrome_options.add_argument('--headless')
            dr = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
        elif USE == Use.AWS.value:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.binary_location = "/opt/chrome/chrome"
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1280x1696')
            chrome_options.add_argument('--single-process')
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-dev-tools")
            chrome_options.add_argument("--no-zygote")
            chrome_options.add_argument('--ignore-certificate-errors')
            chrome_options.add_argument(f'--user-data-dir={mkdtemp()}')
            chrome_options.add_argument(f'--data-path={mkdtemp()}')
            chrome_options.add_argument(f'--disk-cache-dir={mkdtemp()}')
            dr = webdriver.Chrome(service=Service(executable_path="/opt/chromedriver"), options=chrome_options)
        return dr

    def get_available_date(self, dates):
        def is_earlier(date):
            my_date = datetime.strptime(self.my_schedule_date, "%Y-%m-%d")
            new_date = datetime.strptime(date, "%Y-%m-%d")
            result = my_date > new_date
            logger.info(f"Is {my_date} > {new_date}:\t{result}")
            return result
        
        def is_not_today(date):
            new_date = datetime.strptime(date, "%Y-%m-%d")
            today = datetime.today()
            result = new_date != today
            logger.info(f"Is {new_date} not today:\t{result}")
            return result
        
        def is_not_tomorrow(date):
            new_date = datetime.strptime(date, "%Y-%m-%d")
            tomorrow = datetime.today() + timedelta(days=1)
            result = new_date != tomorrow
            logger.info(f"Is {new_date} not tomorrow:\t{result}")
            return result

        logger.info("Checking for an earlier and appropriate date:")
        for d in dates:
            date = d.get('date')
            if is_earlier(date) and is_not_today(date) and is_not_tomorrow(date):
                year, month, day = date.split('-')
                if VisaScheduler.MY_CONDITION_DATE(year, month, day):
                    return date

    @staticmethod
    def send_notification(msg):
        logger.info(f"Sending notification: {msg}")

        if SENDGRID_API_KEY:
            email_recipients = [PRIMARY_EMAIL_RECIPIENT]
            message = Mail(
                from_email=USERNAME,
                to_emails=email_recipients,
                subject=msg,
                html_content=msg)
            try:
                sg = SendGridAPIClient(SENDGRID_API_KEY)
                sg.send(message)
            except Exception as e:
                logger.error(str(e))

        if PUSH_TOKEN:
            url = "https://api.pushover.net/1/messages.json"
            data = {
                "token": PUSH_TOKEN,
                "user": PUSH_USER,
                "message": msg
            }
            requests.post(url, data)

    @staticmethod
    def print_dates(dates):
        logger.info("Available dates:")
        for d in dates:
            logger.info("%s \t business_day: %s" % (d.get('date'), d.get('business_day')))

    def main(self) -> Result:
        # RETRY_TIME
        logger.info(f"---START--- : {datetime.today().strftime('%d/%m/%Y %H:%M:%S')}")

        try:
            self.driver = self.get_driver()
        except WebDriverException as e:
            logger.error(e)
            result = Result.WEBDRIVER_EXCEPTION
            return result

        try:
            self.login()
            self.get_my_schedule_date()
            dates = self.get_date()[:5]
            if not dates:
                logger.info("No dates available on FACILITY")
                result = Result.COOLDOWN
                return result

            self.print_dates(dates)
            date = self.get_available_date(dates)

            if not date:
                # No dates that fulfill MY_CONDITION_DATE or early enough
                result = Result.RETRY
                return result

            date_time = self.get_time(date)

            if not date_time:
                # No times that fulfill MY_CONDITION_TIME
                result = Result.RETRY
                return result

            logger.info(f"New date: {date} {date_time}")

            if NEED_ASC:
                found, asc_date = self.asc_availability(date, date_time)
                if not found:
                    logger.info("No dates available on ASC")
                    result = Result.COOLDOWN
                    return result

                if not asc_date[0] and not asc_date[1]:
                    # No dates that fulfill MY_CONDITION_DATE
                    result = Result.RETRY
                    return result

                if not asc_date[1]:
                    # No times that fulfill MY_CONDITION_TIME
                    result = Result.RETRY
                    return result

                result = self.reschedule(date, date_time, asc_date[0], asc_date[1])
                self.send_notification(f"Earlier date found: {date}")
                result = Result.SUCCESS
            else:
                result = self.reschedule(date, date_time)
                self.send_notification(f"Earlier date found: {date}")
                result = Result.SUCCESS

        except Exception as e:
            logger.error(e)
            result = Result.EXCEPTION

        return result
