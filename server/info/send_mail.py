"""
Should be used but hopeless from behind the proxy. So do the selenium simulation. Costly but works!
"""
import smtplib
import os

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import os

# proxy = 'http://<user>:<pass>@<proxy>:<port>'

# os.environ['http_proxy'] = "http://proxy62.iitd.ac.in:3128" 
# os.environ['HTTP_PROXY'] = "http://proxy62.iitd.ac.in:3128"
# os.environ['https_proxy'] = "https://proxy62.iitd.ac.in:3128"
# os.environ['HTTPS_PROXY'] = "https://proxy62.iitd.ac.in:3128"

import socks

#'proxy_port' should be an integer
#'PROXY_TYPE_SOCKS4' can be replaced to HTTP or PROXY_TYPE_SOCKS5
# socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "https://proxy62.iitd.ac.in", 3128)
# socks.wrapmodule(smtplib)

def main():
	# names, emails = get_contacts('mycontacts.txt') # read contacts
	# message_template = read_template('message.txt')

	# set up the SMTP server
	s = smtplib.SMTP(host='smtpstore.iitd.ac.in', port=587)
	s.starttls()
	s.login("cs5130281@iitd.ac.in", "d9i9zsap")

	# For each contact, send the email:
	# for name, email in zip(names, emails):
	msg = MIMEMultipart()       # create a message

	# add in the actual person name to the message template
	message = "Hello there!!"

	# Prints out the message body for our sake
	print(message)

	# setup the parameters of the message
	msg['To']="sainideepak119@gmail.com"
	msg['From']="cs5130281@iitd.ac.in"
	msg['Subject']="This is TEST"
	
	# add in the message body
	msg.attach(MIMEText(message, 'plain'))
	
	# send the message via the server set up earlier.
	s.send_message(msg)
	del msg
		
	# Terminate the SMTP session and close the connection
	s.quit()
	
if __name__ == '__main__':
	main()