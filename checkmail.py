#!/usr/bin/env python2
import os
import argparse
import requests
import json
import re
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def color(col):
	if col == 'yellow':
		return '\033[93m'
	if col == 'red':
		return '\033[91m'
	if col == 'green':
		return '\033[32m'
	if col == 'cyan':
		return '\033[36m'
	if col == 'magenta':
		return '\033[35m'
	if col == 'end':
		return '\033[0m'

def mailru_check(mailru_domain):
	check_url = 'https://account.mail.ru/api/v1/user/exists'
	payload = 'email='+email+'@'+mailru_domain
	req = requests.get(check_url, timeout = 3, stream = False, verify = False, params = payload)
	resp_json = json.loads(req.content)
	status_bool = str(resp_json.get('body').get('exists'))
	resp_dict = {'True': color('red')+'[-] Email is already use!'+color('end'), 'False': color('green')+'[+] Email is available!'+color('end')}
	status = resp_dict.get(status_bool)
	print u'{0:34} Domain: {1:10}'.format(status,mailru_domain)
	if status_bool == 'True': 
		email_list.append(email+'@'+mailru_domain)

def yandex_session():
	global track_id, yandex_cookie, csrf_token
	headers['x-requested-with'] = 'XMLHttpRequest'
	sess_url = 'https://passport.yandex.ru/registration'
	response = requests.get(sess_url, timeout = 3, stream = False, verify = False, headers = headers)
	soup = BeautifulSoup(response.content, 'html.parser')
	track_id = soup.find_all('input',{'name':'track_id'})[0].get('value')
	csrf_token = re.search('"csrf":"(.+?)"', str(soup)).group(1)
	yandex_cookie = response.cookies.get_dict()

def yandex_check():
	headers['x-requested-with'] = 'XMLHttpRequest'
	check_url = 'https://passport.yandex.ru/registration-validations/login'
	payload = 'track_id='+track_id+'&login='+email+'&csrf_token='+csrf_token
	req = requests.post(check_url, data = payload, timeout = 3, stream = False, verify = False, headers = headers, cookies = yandex_cookie)
	status = req.content
	if 'login.not_available' in status:
		print mail_status.get('0'), 'Domain: yandex.ru'
		email_list.append(email+'@yandex.ru')
		email_list.append(email+'@ya.ru')
	else:
		print mail_status.get('1'), 'Domain: yandex.ru'

def yahoo_session():
	global acrumb, crumb, yahoo_cookie
	headers['X-Requested-With'] = 'XMLHttpRequest'
	sess_url = 'https://login.yahoo.com/account/module/create?specId=yidReg'
	response = requests.get(sess_url, timeout = 3, stream = False, verify = False)
	soup = BeautifulSoup(response.content, "html.parser")
	crumb = soup.find_all('input',{'name':'crumb'})[0].get('value')
	acrumb = soup.find_all('input',{'name':'acrumb'})[0].get('value')
	yahoo_cookie = response.cookies.get_dict()

def yahoo_check():
	global payload, req
	headers['X-Requested-With'] = 'XMLHttpRequest'
	headers['Content-Type'] = 'application/x-www-form-urlencoded'
	check_url = 'https://login.yahoo.com/account/module/create?validateField=yid'
	payload = 'specId=yidreg&crumb='+crumb+'&acrumb='+acrumb+'&yid='+email
	req = requests.post(check_url, data = payload, timeout = 3, stream = False, verify = False, headers = headers, cookies = yahoo_cookie)
	status = req.content
	if 'IDENTIFIER_EXISTS' in status:
		print mail_status.get('0'), 'Domain: yahoo.com'
		email_list.append(email+'@yahoo.com')
	else:
		print mail_status.get('1'), 'Domain: yahoo.com'

def gmail_session():
	global result
	sess_url = 'https://accounts.google.com/signup/v2/webcreateaccount?service=mail&flowEntry=SignUp'
	response = requests.get(sess_url, timeout = 3, stream = False, verify = False)
	soup = BeautifulSoup(response.content, "html.parser")
	parse=soup.find_all('div',{"class": "JhUD8d SQNfcc vLGJgb"})[0].get('data-initial-setup-data')
	result=parse.split(',')[13]

def gmail_check():
	global status
	headers['Google-Accounts-Xsrf'] = '1'
	headers['Content-Type'] = 'application/x-www-form-urlencoded'
	check_url = 'https://accounts.google.com/_/signup/webusernameavailability'
	payload = 'f.req=['+result+',"","","'+email+'"]'
	req = requests.post(check_url, data = payload, timeout = 3, stream = False, verify = False, headers = headers)
	status = req.content
	check_status = status.split(',')[1]
	resp_dict = {'2': color('red')+'[-] Email is already use!'+color('end'), '1': color('green')+'[+] Email is available!'+color('end')}
	status = resp_dict.get(check_status)
        print u'{0:34} Domain: {1:10}'.format(status,'gmail.com')
	if check_status == '2':
		email_list.append(email+'@gmail.com')

def rambler_check(rambler_domain):
	headers['Content-Type'] = 'application/json'
	check_url = 'https://id.rambler.ru/jsonrpc'
	payload = '{"rpc":"2.0","method":"Rambler::Id::login_available","params":[{"login":"'+email+'@'+rambler_domain+'"}]}'
	req = requests.post(check_url, data = payload, timeout = 3, stream = False, verify = False, headers = headers)
	status = req.content
	if '"strerror":"user not exist"' in status:
		print mail_status.get('1'), 'Domain:',rambler_domain
	else:
		print mail_status.get('0') , 'Domain:',rambler_domain
		email_list.append(email+'@'+rambler_domain)


parser = argparse.ArgumentParser(description='Example: %(prog)s --email username', usage='%(prog)s --email username')
parser.add_argument("-e", "--email", help='Username for check email available on yandex, mail, gmail, rambler, yahoo')
args = parser.parse_args()
email = args.email

os.system('clear')

headers = {'UserAgent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36'}
mail_status = {'0': color('red')+'[-] Email is already use!'+color('end'), '1': color('green')+'[+] Email is available!  '+color('end')}
email_list = []
print color('cyan')+'-------------------------------------------------'+color('end')
print color('magenta')+'             EXISTENCE EMAIL CHECKER'+color('end')
print color('cyan')+'-------------------------------------------------'+color('end')

if email is None:
	print color('red')+"Run script option -h"+color('end')
	os._exit(0)

print 'Check email: ', color('yellow')+email+color('end')

print color('cyan')+'-------------------YANDEX.RU---------------------'+color('end')
yandex_session()
yandex_check()

print color('cyan')+'--------------------MAIL.RU----------------------'+color('end')
mailru_domains = ['mail.ru','bk.ru','inbox.ru','list.ru','internet.ru']
for domain in mailru_domains:
	mailru_check(domain)

print color('cyan')+'-------------------GMAIL.COM---------------------'+color('end')
gmail_session()
gmail_check()

print color('cyan')+'------------------RAMBLER.RU---------------------'+color('end')
rambler_domains = ['rambler.ru','lenta.ru','autorambler.ru','myrambler.ru','ro.ru']
for domain in rambler_domains:
	rambler_check(domain)

print color('cyan')+'------------------YAHOO.COM----------------------'+color('end')
yahoo_session()
yahoo_check()

print color('cyan')+'-------------------------------------------------'+color('end')

print ('All emails:')
print email_list
