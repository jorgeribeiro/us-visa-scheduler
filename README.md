# US Visa Scheduler

## How to run locally
- Install the required python packages: `pip install -r requirements.txt`
- Simply run `python -c "import setup; setup.as_loop()"`

## Next steps
- Test!
- Implement blacklisted dates
- Implement useful email notifications:
    - Successful reschedule
    - Failed login attempt
    - Execution stopped since interview date is nearby
    - Any failures or unexpected results sent to the developer's email
- Use Serverless Framework to facilitate the deployment

## Extra notes
```
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
```