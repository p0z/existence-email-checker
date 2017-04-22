#!/usr/bin/env python
import os
import argparse
import requests
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

def mailru_session():
	global email_inp, reg_id
	sess_url = 'https://e.mail.ru/signup?from=main_noc'
	response = requests.get(sess_url, timeout = 3, stream = False, verify = False, headers = headers)
	soup = BeautifulSoup(response.content, "html.parser")
	email_inp = soup.find_all('span',{'class':'sig2 tal pRel'})[0].contents[1].get('name')
	reg_id = soup.find_all('input',{'name':'x_reg_id'})[0].get('value')

def mailru_check(mailru_domain):
	check_url = 'https://e.mail.ru/cgi-bin/checklogin'
	payload = 'RegistrationDomain='+mailru_domain+'&'+email_inp+'='+email+'&'+'x_reg_id='+reg_id
	req = requests.post(check_url, data = payload, timeout = 3, stream = False, verify = False, headers = headers)
	resp_dict = {'EX_USEREXIST': color('red')+'[-] Email is already use!'+color('end'), '0': color('green')+'[+] Email is available!'+color('end'), '109': color('magenta')+'[X] Error! (maybe reg_id is not correct)'+color('end'), 'EX_INVALIDUSERNAME': color('magenta')+'[X] Error! (invalid username)'+color('end'), '108': color('magenta')+'[X] Error! (banned)'+color('end')}
	status = resp_dict.get(req.content)
	print u'{0:34} Domain: {1:10}'.format(status,mailru_domain)

def yandex_session():
	global track_id
	headers['x-requested-with'] = 'XMLHttpRequest'
	sess_url = 'https://passport.yandex.ru/registration'
	response = requests.get(sess_url, timeout = 3, stream = False, verify = False, headers = headers)
	soup = BeautifulSoup(response.content, "html.parser")
	track_id = soup.find_all('input',{'name':'track_id'})[0].get('value')

def yandex_check():
	headers['x-requested-with'] = 'XMLHttpRequest'
	check_url = 'https://passport.yandex.ru/registration-validations/login'
	payload = 'track_id='+track_id+'&login='+email
	req = requests.post(check_url, data = payload, timeout = 3, stream = False, verify = False, headers = headers)
	status = req.content
	if 'login.not_available' in status:
		print mail_status.get('0'), 'Domain: yandex.ru'
	else:
		print mail_status.get('1'), 'Domain: yandex.ru'

def yahoo_session():
	global crumb, yahoo_cookie
	headers['x-requested-with'] = 'XMLHttpRequest'
	sess_url = 'https://login.yahoo.com/account/module/create?specId=yidReg'
	response = requests.get(sess_url, timeout = 3, stream = False, verify = False)
	soup = BeautifulSoup(response.content, "html.parser")
	crumb = soup.find_all('input',{'name':'crumb'})[0].get('value')
	yahoo_cookie = response.cookies.get_dict()

def yahoo_check():
	headers['X-Requested-With'] = 'XMLHttpRequest'
	headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
	check_url = 'https://login.yahoo.com/account/module/create?validateField=yid'
	payload = 'specId=yidReg&crumb='+crumb+'&yid='+email
	req = requests.post(check_url, data = payload, timeout = 3, stream = False, verify = False, headers = headers, cookies = yahoo_cookie)
	status = req.content
	if 'IDENTIFIER_EXISTS' in status:
		print mail_status.get('0'), 'Domain: yahoo.com'
	else:
		print mail_status.get('1'), 'Domain: yahoo.com'

def gmail_check():
	headers['Content-Type'] = 'application/json'
	check_url = 'https://accounts.google.com/InputValidator?resource=SignUp'
	payload = '{"input01":{"Input":"GmailAddress","GmailAddress":"'+email+'","FirstName":"","LastName":""},"Locale":"ru"}'
	req = requests.post(check_url, data = payload, timeout = 3, stream = False, verify = False, headers = headers)
	status = req.content
	if '"Valid":"false"' in status:
		print mail_status.get('0'), 'Domain: gmail.com'
	else:
		print mail_status.get('1'), 'Domain: gmail.com'

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


parser = argparse.ArgumentParser(description='Example: %(prog)s --email username', usage='%(prog)s --email username')
parser.add_argument("-e", "--email", help='Username for check email available on yandex, mail, gmail, rambler, yahoo')
args = parser.parse_args()
email = args.email

os.system('clear')

headers = {'UserAgent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36'}
mail_status = {'0': color('red')+'[-] Email is already use!'+color('end'), '1': color('green')+'[+] Email is available!  '+color('end')}

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
mailru_domains = ['mail.ru','bk.ru','inbox.ru','list.ru']
mailru_session()
for domain in mailru_domains:
	mailru_check(domain)

print color('cyan')+'-------------------GMAIL.COM---------------------'+color('end')
gmail_check()

print color('cyan')+'------------------RAMBLER.RU---------------------'+color('end')
rambler_domains = ['rambler.ru','lenta.ru','autorambler.ru','myrambler.ru','ro.ru']
for domain in rambler_domains:
	rambler_check(domain)

print color('cyan')+'------------------YAHOO.COM----------------------'+color('end')
yahoo_session()
yahoo_check()

print color('cyan')+'-------------------------------------------------'+color('end')


