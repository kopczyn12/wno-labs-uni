from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import random
import string
import time

def create_mail(phone_number: str):
    # Replace the path below with the path to your ChromeDriver executable
    driver_path = '/home/mkopcz/Desktop/uni/wno2/lab2/chromedriver'
    driver = webdriver.Chrome(driver_path)
    chrome_path = '/usr/bin/chromium-browser'
    # Set the Chromium binary path in the options
    options = webdriver.ChromeOptions()
    options.binary_location = chrome_path
    
    # Navigate to the Gmail signup page
    driver.get('https://accounts.google.com/signup')

    # Generate a random username
    letters = string.ascii_lowercase
    username = ''.join(random.choice(letters) for i in range(10))

    # Enter the username into the username field
    username_field = driver.find_element_by_name('firstName')
    username_field.send_keys(username)

    # Generate a random password
    password = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(10))

    # Enter the password into the password field
    password_field = driver.find_element_by_name('Passwd')
    password_field.send_keys(password)

    # Confirm the password by re-entering it
    confirm_password_field = driver.find_element_by_name('ConfirmPasswd')
    confirm_password_field.send_keys(password)

    # Enter the phone number into the phone number field
    phone_field = driver.find_element_by_name('phoneNumber')
    phone_field.send_keys('+' + phone_number)

    # Click the Next button
    next_button = driver.find_element_by_xpath('//*[@id="accountDetailsNext"]/div/button/span')
    next_button.click()

    # Wait for the phone verification page to load
    time.sleep(5)

    # Click the Skip button to bypass phone verification
    skip_button = driver.find_element_by_xpath('//*[@id="view_container"]/div/div/div[2]/div/div[2]/div/div[1]/div/content/span')
    skip_button.click()

    # Wait for the account creation to finish
    time.sleep(5)

    # Close the browser window
    driver.quit()

    # Print the username and password for reference
    print('Mail has been created!')
    print('Username: ' + username)
    print('Password: ' + password)

create_mail('48603036631')
