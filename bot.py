from selenium import webdriver
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import configparser
from utility_methods.utility_methods import *
import urllib.request
from InstagramAPI import InstagramAPI
import logging


class InstagramBot:
    def __init__(self, username = None, password = None):
        """
        Initializes an instance of the InstagramBot class.
        
        Args: 
            username:str: The Instagram username for a user
            password:str: The Instagram password for a user

            Attributes:
            driver:Selenium.webdriver.Chrome: The Chromedriver that is used to automate browser actions
            login: the URL to login to IG
            nav_url: the URL to get to the home page of a user on IG
            tag_url: the URL to get posts with a certain tag
            stay_logged: The boolean to find our whether the current user should stay logged in

        """
        self.username = config['AUTH']['USERNAME']
        self.password = config['AUTH']['PASSWORD']
        self.login = config['URL']['LOGIN']
        self.nav_url = config['URL']['NAV']
        self.tag_url = config['URL']['TAGS']
        self.direct_url = config['URL']['DM']
        self.driver = webdriver.Chrome(config['ENVIRONMENT']['CHROMEDRIVER'])
        self.stay_logged = False
        self.api = InstagramAPI(self.username, self.password)

    # Tested
    @sleep_method
    def login(self):
        """
            Method allows user to log in through the web

        """
        self.driver.get(self.login)
        PAUSE = 2
        time.sleep(PAUSE)
        user_input = self.driver.find_element_by_name('username')
        pass_input = self.driver.find_element_by_name('password')
        login_button = self.driver.find_elements_by_xpath("//div[contains(text(),'Log In')]")[0]
        user_input.send_keys(self.username)
        pass_input.send_keys(self.password)
        login_button.click()
        time.sleep(PAUSE)

    # Tested
    @sleep_method
    def nav_user(self, user):
        """
            Method allows users to navigate through a user's profile page

        """
        self.driver.get(self.nav_url.format(user))
    
    # Tested
    @sleep_method
    def search_tag(self, tag):
        """
           Method goes to posts with a specific tag

        """
        self.driver.get(self.tag_url.format(tag))

    # Tested
    @sleep_method
    def follow_user(self, user):
        """
            Method follows user

        """
        self.nav_user(user)
        follow_button = self.find_buttons('Follow')
        for button in follow_button:
            button.click()
    
    # Tested
    @sleep_method
    def unfollow_user(self, user):
        """
            Method unfollows user

        """
        self.nav_user(user)
        unfollow_button = self.driver.find_elements_by_xpath('/html/body/div[1]/section/main/div/header/section/div[1]/div[2]/div/span/span[1]/button')
        if unfollow_button:
            for button in unfollow_button:
                button.click()
                unfollow_confirm = self.find_buttons('Unfollow')[0]
                unfollow_confirm.click()
        else:
            print('No {} buttons were found.'.format('Following'))
    
    @sleep_method
    def direct_message(self, user, msg, num):
        """
            Method allows bot to automatically type and send dm to user

        """
        PAUSE = 1
        logging.info('Send message {} to {}'.format(msg,user))
        self.driver.get(self.direct_url)
        self.driver.find_elements_by_xpath('/html/body/div[2]/div/div/div[2]/div[1]/div/div[2]/input')[0].send_keys(user)
        time.sleep(PAUSE)
        self.driver.find_elements_by_xpath('/html/body/div[5]/div/div/div/div[3]/button[2]')[0].click() #Edge case to get rid of notification
        time.sleep(PAUSE)
        self.driver.find_elements_by_xpath('/html/body/div[2]/div/div/div[2]/div[2]/div/div/div[3]/button')[0].click()
        self.driver.find_elements_by_xpath('/html/body/div[2]/div/div/div[1]/div/div[2]/div/button')[0].click()
        time.sleep(PAUSE)
        # The message will be placed and sent
        self.driver.find_elements_by_xpath('//*[@id="react-root"]/section/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[2]/textarea')[0].send_keys(msg)
        time.sleep(PAUSE)
        self.driver.find_elements_by_xpath('//*[@id="react-root"]/section/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[3]/button')[0].click()
        # Special feature involving reacting with heart
        for x in range(num):
            self.driver.find_elements_by_xpath('//*[@id="react-root"]/section/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/button[2]')[0].click()
            time.sleep(PAUSE)
    
    # Tested
    def find_buttons(self, button_txt):
        """
            Method finds the button to follow or unfollow users.
            It filters the follow elements to find buttons.
            The default method looks for only follow buttons.
        """
        button = self.driver.find_elements_by_xpath("//*[text()='{}']".format(button_txt))
        return button

    # Tested
    @sleep_method
    def latest_likes(self, user, number_posts, likes):
        """
            Method likes a specific number of a user's posts.

        """
        WAIT = 1
        if likes:
            action = 'Like'
        else:
            action = 'Unlike'
        self.nav_user(user)
        image_container = []
        image_container.extend(self.driver.find_elements_by_class_name('_9AhH0'))
        for image in image_container[:number_posts]:
            image.click()
            time.sleep(WAIT)
            try:
                self.driver.find_element_by_xpath("//*[@aria-label='{}']".format(action).click())
            except Exception as e:
                print(e)
            self.driver.find_elements_by_xpath('/html/body/div[4]/div[2]/div/article/div[3]/section[1]/span[1]/button')[0].click() # clicks the heart symbol
            time.sleep(WAIT)
            self.driver.find_elements_by_xpath('/html/body/div[4]/div[3]/button')[0].click() #Makes sure to close out of current picture
            time.sleep(WAIT)
        
        # Tested
        users_list = []
        def get_likes_list(self, username):
            """
                Method gets a list of users who like a post

            """
            api = self.api
            api.searchUsername(username) 
            result = api.LastJson
            username_id = result['user']['pk'] #Gets the user ID
            user_posts = api.getUserFeed(username_id) # gets the user feed
            result = api.LastJson
            media_id = result['items'][0]['id'] #gets the most recent post
            api.getMediaLikers(media_id) #gets users who liked
            users = api.LastJson('users')
            for user in users: #appends the users to the list
                users_list.append({'pk':user['pk'], 'username':user['username']})


if __name__ == '__main__':
    config_path = './config.ini'
    logger_path = './bot.log'
    config = config_init(config_path)
    log = get_log_object(logger_path)
    bot = InstagramBot("","")
    # Tests
    # InstagramBot.login(bot)
    # InstagramBot.follow_user(bot, "sumedhchilak")
    # InstagramBot.unfollow_user(bot, "sumedhchilak")
    # InstagramBot.like_list(bot,'instagram')
    # bot.latest_likes('sumedhchilak', 5, likes = True)
    # InstagramBot.search_tag(bot, 'School')
    # bot.direct_message('sumedhchilak', 'hey', 5)



    
