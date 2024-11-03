# -*- coding: utf8 -*-
import configparser
import logging
import os
import random
import re
import sys
import time as tm
from datetime import datetime, timedelta
from enum import Enum
from tempfile import mkdtemp

import gspread
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException
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

BLACKLISTED_DATES = config['BLACKLISTED_DATES']

SENDGRID_API_KEY = config['SENDGRID']['SENDGRID_API_KEY']
PRIMARY_EMAIL_RECIPIENT = config['SENDGRID']['PRIMARY_EMAIL_RECIPIENT']
PUSH_TOKEN = config['PUSHOVER']['PUSH_TOKEN']
PUSH_USER = config['PUSHOVER']['PUSH_USER']
SPREADSHEET_ID = config['GOOGLE_SHEETS']['SPREADSHEET_ID']

USE = config['ENVIRONMENT']['USE']
TIMEZONE = config['ENVIRONMENT']['TIMEZONE']

REGEX_CONTINUE = "//a[contains(text(),'Continue')]"

STEP_TIME = 0.5  # time between steps (interactions with forms)

DATE_URL = f"https://ais.usvisa-info.com/{COUNTRY_CODE}/niv/schedule/{SCHEDULE_ID}/appointment/days/{FACILITY_ID}.json?appointments[expedite]=false"
TIME_URL = f"https://ais.usvisa-info.com/{COUNTRY_CODE}/niv/schedule/{SCHEDULE_ID}/appointment/times/{FACILITY_ID}.json?date={{date}}&appointments[expedite]=false"
HOME_URL = f"https://ais.usvisa-info.com/{COUNTRY_CODE}/niv/account"
APPOINTMENT_URL = f"https://ais.usvisa-info.com/{COUNTRY_CODE}/niv/schedule/{SCHEDULE_ID}/appointment"
DATE_URL_ASC = f"https://ais.usvisa-info.com/{COUNTRY_CODE}/niv/schedule/{SCHEDULE_ID}/appointment/days/{ASC_ID}.json?&consulate_id={FACILITY_ID}&consulate_date={{date}}&consulate_time={{time}}&appointments[expedite]=false"
TIME_URL_ASC = f"https://ais.usvisa-info.com/{COUNTRY_CODE}/niv/schedule/{SCHEDULE_ID}/appointment/times/{ASC_ID}.json?date={{date_asc}}&consulate_id={FACILITY_ID}&consulate_date={{date}}&consulate_time={{time}}&appointments[expedite]=false"

class Use(Enum):
    AWS = "AWS"
    LOCAL = "LOCAL"

class VisaScheduler:
    def __init__(self):
        self.my_schedule_date = None
        os.environ['TZ'] = TIMEZONE
        tm.tzset()

    def get_header(self):
        return {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": self.driver.execute_script("return navigator.userAgent;"),
            "Referer": APPOINTMENT_URL,
            "Cookie": "_yatri_session=" + self.driver.get_cookie("_yatri_session")["value"]
        }

    def get_my_schedule_date(self):
        self.driver.get(HOME_URL) # Go to home page where schedule date is displayed
        element = self.driver.find_element(By.XPATH,
                                           '//a[contains(@href, "%s")]/ancestor::div[contains(@class, "application")]' % SCHEDULE_ID)

        appointment = element.find_element(By.CLASS_NAME, 'consular-appt').text
        regex = r".+: (.+,.+),.+"
        date = re.search(regex, appointment).group(1)
        return datetime.strptime(date, "%d %B, %Y").strftime("%Y-%m-%d")
    
    def is_schedule_date_near(self):
        my_schedule_date = datetime.strptime(self.my_schedule_date, "%Y-%m-%d")
        today = datetime.today()
        delta = my_schedule_date - today
        return delta.days <= 7

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

    def get_appointment_dates(self):
        if not self.is_logged_in():
            self.login()
            return self.get_appointment_dates()
        else:
            logger.info("Getting dates...")
            r = requests.get(DATE_URL, headers=self.get_header())
            if r.status_code == 401:
                print("Unauthorized. Logging back in...")
                self.login()
                return self.get_appointment_dates()
            
            dates = r.json()
            return dates

    def get_time(self, date):
        time_url = TIME_URL.format(date=date)
        r = requests.get(time_url, headers=self.get_header())
        data = r.json()
        times = data.get("available_times")[::-1]
        for t in times:
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
        requests.post(APPOINTMENT_URL, headers=headers, data=data)
        logger.info("Reschedule attempt complete.")

        schedule_date = self.get_my_schedule_date()
        if schedule_date == date:
            msg = f"[{USERNAME}] Rescheduled Successfully! {date} {time}"
            logger.info(msg)
            self.send_notification(msg)
            return Result.SUCCESSFUL_RESCHEDULE
        else:
            msg = f"[{USERNAME}] Reschedule Failed. {date} {time}"
            logger.error(msg)
            self.send_notification(msg)
            return Result.FAILED_RESCHEDULE

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
            dr = webdriver.Chrome(service=Service(executable_path=ChromeDriverManager().install()), options=chrome_options)
        elif USE == Use.AWS.value:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.binary_location = "/opt/chrome/chrome"
            chrome_options.add_argument('--headless=new')
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
            chrome_options.add_argument("--remote-debugging-port=9222")
            chrome_options.add_argument('user-agent={0}'.format('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36'))
            dr = webdriver.Chrome(service=Service(executable_path="/opt/chromedriver"), options=chrome_options)
        return dr

    def get_available_date(self, dates):
        blacklisted_dates = []
        for _, value in BLACKLISTED_DATES.items():
            date_range = value.split(',')
            start_date = datetime.strptime(date_range[0].strip(), '%Y-%m-%d')
            end_date = datetime.strptime(date_range[-1].strip(), '%Y-%m-%d') + timedelta(days=1)
            while start_date < end_date:
                blacklisted_dates.append(start_date.strftime('%Y-%m-%d'))
                start_date += timedelta(days=1)

        def is_earlier(date):
            my_date = datetime.strptime(self.my_schedule_date, "%Y-%m-%d")
            new_date = datetime.strptime(date, "%Y-%m-%d")
            result = my_date > new_date
            logger.info(f"Is {my_date} > {new_date}:\t{result}")
            return result

        logger.info("Checking for an earlier date:")
        for d in dates:
            date = d.get('date')
            if is_earlier(date) and not date in blacklisted_dates:
                return date

    @staticmethod
    def send_notification(msg):
        logger.info(f"Sending notification: {msg}")

        if SENDGRID_API_KEY:
            email_recipients = [PRIMARY_EMAIL_RECIPIENT]
            message = Mail(
                from_email=PRIMARY_EMAIL_RECIPIENT,
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
    def write_result_to_gsheet(execution_timestamp, earliest_date, result):
        if not SPREADSHEET_ID:
            return
        try:
            gc = gspread.service_account(filename='keyfile.json')
            sh = gc.open_by_key(SPREADSHEET_ID).sheet1
            number_of_rows = len(sh.col_values(1))
            if number_of_rows >= 150: # If the sheet has 150+ rows, delete all rows but the header
                sh.batch_clear([f"A2:C{number_of_rows}"])
            sh.append_row([execution_timestamp, earliest_date, result])
        except Exception:
            return

    @staticmethod
    def print_dates(dates):
        logger.info("Available dates:")
        for d in dates:
            logger.info("%s \t business_day: %s" % (d.get('date'), d.get('business_day')))

    def main(self) -> Result:
        execution_timestamp = datetime.today().strftime('%d/%m/%Y %H:%M:%S')
        logger.info(f"---START--- : {execution_timestamp} for {USERNAME}")

        try:
            self.driver = self.get_driver()
        except WebDriverException as e:
            logger.error(e)
            return Result.WEBDRIVER_EXCEPTION

        try:
            self.login()
        except TimeoutException as e:
            logger.error(e)
            return Result.EXCEPTION

        try:
            logger.info("Getting current schedule date...")
            self.my_schedule_date = self.get_my_schedule_date()
            logger.info(f"Current schedule date: {self.my_schedule_date}")

            if (self.is_schedule_date_near()):
                msg = f"[{USERNAME}] Current date: {self.my_schedule_date} is near enough. Stopping..."
                logger.info(msg)
                self.send_notification(msg)
                return Result.STOP

            dates = self.get_appointment_dates()[:5]
            if not dates:
                logger.info("No dates available on FACILITY")
                self.write_result_to_gsheet(execution_timestamp, 'None', Result.COOLDOWN.value)
                return Result.COOLDOWN

            earliest_date = dates[0].get('date')
            self.print_dates(dates)
            date = self.get_available_date(dates)
            if not date:
                self.write_result_to_gsheet(execution_timestamp, earliest_date, Result.RETRY.value)
                return Result.RETRY

            date_time = self.get_time(date)
            if not date_time:
                self.write_result_to_gsheet(execution_timestamp, earliest_date, Result.RETRY.value)
                return Result.RETRY

            logger.info(f"New date: {date} {date_time}")

            if NEED_ASC:
                found, asc_date = self.asc_availability(date, date_time)
                if not found:
                    logger.info("No dates available on ASC")
                    self.write_result_to_gsheet(execution_timestamp, 'None', Result.COOLDOWN.value)
                    return Result.COOLDOWN

                if not asc_date[0] and not asc_date[1]:
                    self.write_result_to_gsheet(execution_timestamp, 'None', Result.RETRY.value)
                    return Result.RETRY

                if not asc_date[1]:
                    self.write_result_to_gsheet(execution_timestamp, 'None', Result.RETRY.value)
                    return Result.RETRY

                result = self.reschedule(date, date_time, asc_date[0], asc_date[1])
                self.send_notification(f"[{USERNAME}] Earlier date found: {date}")
            else:
                result = self.reschedule(date, date_time)
                self.send_notification(f"[{USERNAME}] Earlier date found: {date}")
            self.write_result_to_gsheet(execution_timestamp, date, result.value)
        except Exception as e:
            logger.error(e)
            result = Result.EXCEPTION

        return result
