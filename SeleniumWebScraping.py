#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 08:42:14 2017


Notes:
    Some basic webscraping with Selenium
    This is NOT an optimal or particularly reliable way to do things, but there are instances where
        there is quite literally no other automated way possible (ie: when files need to be exported)

Dependencies:
    You must have the proper Chromedriver executable in your working directory
    You can avoid this by using PhantomJS, which is a headless browser, but using that can often
        make it extremely hard to debug, or have unexpected results
"""

#==============================================================================
# Package imports
#==============================================================================
from selenium import webdriver
import glob
import os, time
import pandas as pd

# Point to your Chromedriver executeable
chromedriver = os.path.dirname(os.path.realpath(__file__)) + '/chromedriver'

# Set the environment variable to your Chromedriver path
os.environ["webdriver.chrome.driver"] = chromedriver

# Initialize a Chrome browser with the desired options
chromeOptions = webdriver.ChromeOptions()
prefs = {"download.default_directory" : os.path.realpath(__file__),
        "download.prompt_for_download":  False,
        "profile.content_settings.pattern_pairs.*.multiple-automatic-downloads": 1,
        "profile.content_settings.exceptions.automatic_downloads.*.setting": 1}
chromeOptions.add_experimental_option("prefs",prefs)
browser = webdriver.Chrome(executable_path=chromedriver, chrome_options=chromeOptions)

# Navigate to your initial URL
browser.get('https://myurl.com')

# Instruct the script to wait while the server responds
# This may need some tweaking depending on the website's servers/your internet connection
# You will want to put some form of script waiting function between your navigations
time.sleep(0.5)

# Example of populating username and password fields to textbox elements
username = browser.find_element_by_class_name("username-field")
password = browser.find_element_by_class_name("password-field")
username.send_keys('username')
password.send_keys('password')

# Example of clicking a login button
browser.find_element_by_css_selector("login_button").click()

# You can get attributes of elements to access buried HTMl values
date_value = browser.find_element_by_name('maybe_a_date_range_field').get_attribute('value')

# Example of returning more than one element to iterate through if they share a common css tag
not_li_list = browser.find_elements_by_css_selector('list_of_elements_tags')

# Get all the files in a directory based on a common identifier (file extension, title, etc.)
allFiles = glob.glob(os.path.realpath(__file__) + "/your_file_commonality*.csv")

# Initialize empty DataFrame and list
frame = pd.DataFrame()
list_ = []

# Iterate through each file and read in (for this example, csvs) data to temp DataFrame object
# Append each of these file DataFrames to a list
for file_ in allFiles:
    df = pd.read_csv(file_, index_col=None)
    list_.append(df)

# Smush all the dataframes in the list together into one big DataFrame!
frame = pd.concat(list_)

# Delete al downloaded files from directory
for f in glob.glob("your_file_commonality*.csv"):
    os.remove(f)