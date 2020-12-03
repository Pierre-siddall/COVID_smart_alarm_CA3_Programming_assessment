# COVID_smart_alarm
# Introduction
The purpose of this project was to create a smart alarm clock which briefs users on the daily 
cases and deaths during the ongoing coronavirus pandemic. This code was written as part of a continuous assessment on the ECM1400 programming module, at the University of Exeter.
### Prerequisites
To be able to run this program effectively the following prerequisites are needed:
- An installation of python 3.9
- A good internet connection that can access web services 
- your own API keys for https://openweathermap.org and https://newsapi.org/

### Installation
This module relies on the following module dependencies:
- requests
- pyttsx3
- uk_covid19
- flask

Here is how you install each of the dependencies above:
```sh
$ pip install requests
```
```sh
$ pip install pyttsx3
```
```sh
$ pip install uk_covid19
```
```sh
$ pip install flask 
```
### Getting started 
To get started with this module you need to firstly enter the preference for your news source and your location upon the apps start up.This ensures that the breifings and notifications recived can be tailored to match your needs. To schedule your first briefing enter the date and time in the topmost input field then enter the name of your alarm below it. After this click the submit button to register your alarm into the application. Please be aware that the page reloads every minute, meaning that you have one minute to register an alarm before the data in the input field is erased and you have to retype it again.
### Testing 
To run the code firstly start either start a command line interface and type: 
```sh
$ python3 COVID_smart_alarm.py
```
or copy and paste the code into an IDLE and run it.The user should then navigate to http://127.0.0.1:5000/ to start the application.This module also comes with a function that performs unit tests.
```python
def tests():
    """This function tests the functionality of my other functions using 
    assertion"""
    numbers_upto_ten = {'01': '1', '02': '2', '03': '3', '04': '4',
                        '05': '5', '06': '6', '07': '7', '08': '8', '09': '9'}
    # Here assertions are used as unit tests for my code
    assert get_right_date_numbers(
        "2020-12-02", numbers_upto_ten) == (2020, 12, 2)
    assert get_right_date_numbers(
        "2020-02-01", numbers_upto_ten) == (2020, 2, 1)
    assert get_right_date_numbers(
        "2020-12-25", numbers_upto_ten) == (2020, 12, 25)
    assert get_day_difference("2020-12-02", "2020-12-25") == 23
    assert get_day_difference("2020-12-02", "2020-12-02") == 1
    assert get_day_difference("2020-12-02", "2020-11-01") == None
    assert get_coronavirus_data_test() == 'K02000001'
    assert get_news_test() == 'ok'
    assert get_weather_test('Exeter') == 200
```
Calling this function in the program checks to see whether the APIs are functioning correctly by seeing if they return either the excpected area code (covid API), the expected status message (news API) and the expected numerical status code (weather API).This unit test also tests to see if the right date numbers are returned by the get_right_date_numbers() function which returns the numerical value of the year,month and day of date in decimal format which the computer can read (converting the numbers 01-09 to a single digit and keeping the values above 09 as double digits). Finally the unit test checks to see if the correct day difference that is to be used in the program is returned throught the get_day_difference() function.The significance of why the lowest numerical value that can be returned is 1, is disscused in the developer documentation.
#### Developer documentation 
The following developer documentation includes the names of the functions in the module and their respective docstrings. Any addtional comments are made below each of the functions.
```python
def create_log() -> None:
    """This function configures the log file by determining the format of log messages and initialising the log file """
```
The create _log function makes use of the logging module to keep track of events within the program. create_log() sets the format in which the log file is to be recorded and creates/opens the log file by using:
```python 
    logging.basicConfig(format=FORMAT, filename='pyapp.log',
                        level=logging.DEBUG)
```
The format parameter sets the format of the file. The filename parameter sets the log files name and the level parameter determines the highest level of an event that  can be recorded in the log file.
```python
def announcement(text: str) -> None:
    """This function takes in a piece of text as a string then initialises the text to speech engine to say the text passed as a paremeter to the function"""
```
The announcement function makes use of the pyttsx3 module to create an engine so that the text parameter (which is input as a string) can be spoken out loud (translated to speech) by the device on which the code is running on.
```python
def get_weather(location: str) -> list:
    """This function begins by taking in a location as a string, which is predefined by the user 
    upon the apps start up.The function then proceeds to read to config file to get an api key .
    This api key is used to get the weather data which is returned in a json format.The required data 
    is then extracted from the json object and returned in a list to be used elsewhere a piece of code"""
```
The get_weather function uses the config file the grab an API key for https://openweathermap.org and takes in the location parameter as a string.This location parameter which the user input upon the applications start up allows for weather data for the users location to be returned by the API.The function then filters the json object returned by the API to extract relevant information about the weather in the users chosen location. 
```python
def get_news(*args: str) -> list:
    """Similar to the get_weather() function this function begins by taking in multiple arguments as a string, which is predefined by the user 
    upon the apps start up.The function then proceeds to read to config file to get an api key .
    This api key is used to get current news headlines which are returned in a json format.Then the code 
    goes through all the articles in the json object and appends articles with any of the arguments passed into the get news function to a filtered articles list.
    This list is then returned."""
```
The get_news function takes in arguments defined by the user on startup and queries the https://newsapi.org/ API  by using the specified key in the config file.The get_news function then returns a list of articles containing the arguments passed into the function.
```python
def get_coronavirus_data() -> list:
    """This function begins by using the config file to get the filters it needs to pass to Cov19API.The function then queries the goverment 
    covid19 api with the appropriate filters returning them as a json object.The relevant pieces of information are then extracted from the json 
    object and are returned in a list"""
```
The get_coronavirus_data function gets the relevant filters from the config file and queries the covid19 API using the Cov19 function from the uk_covid19 module.The program also sets the area type to an overview using this line of code:
```python
overview = ['areaType=overview']
```
which tells the API to get data for the whole of the uk.
```python
def breifing(date_time: str, chosen_news: str, chosen_weather: str, hasweather: bool = False, hasnews: bool = False) -> None:
    """This function takes in several parameters which form the briefing messages through data stored in the config file and 
    data returned by the APIs.The function then removes the appropriate alarm from the list of dictionaries and reads out a 
    breifing according to the users preferences when setting the alarm"""
```
The parameters for date_time, chosen_news and chosen_weather are all to be passed as strings. The date_time parameter holds the date and time that an alarm was set this is the ensure that the alarm can be removed from the user_alarms list once the briefing has triggered. The chosen_news and chosen_weather parameters take in the user preferences for news website and weather location of a user. Finally the hasweather and hasnews parameters are taken in as boolean values this is to indicate to the function that the user either wants weather in their briefing and/or wants news in their briefing.If they want weather or news the value of hasweather or hassnews is set to true accordingly otherwise these values are set to false. 
```python
def populate_notifications(note_list: list, chosen_news: str) -> None:
    """This function makes API calls to the coronavirus and news API.The function then 
    appends the articles that have been filtered to a notifications list.The function also 
    checks the coronavirus data and adds a notification to the notifications list to indidicate 
    that a  certain threshold (in number of cases) has been passed. Notifications are added 
    to the notifications list in the format of a dictionary"""
```
The populate_notifications function calls in populates a nottification list as defined by the note_list parameter with the filtered articles recived by the get_news function.It also adds notifications to the notifications list to show when certain cornavirus case thresholds have been passed as defined by the get_coronavirus_data function. 
```python
def get_right_date_numbers(date: str, dictionary: dict) -> int:
    """This function gets the correct date number that can be used in the program.
    As numbers repsesented by 01-09 break the program there fore this function handles 
    this issue by looking to see if those valuse are in the keys of a dictionary passed into the function
    if so then the day and/or the month are assinged its correct value"""
```
Here the get_right_date_numbers() function is used to make sure that numbers begining with a zero are represented as single digits so that the date objects which are called in the get_day_diffrence() function work as intended.
```python
def get_day_difference(date1: str, date2: str) -> int:
    """This function claclates the diffrence of days inbetween two dates passed as strings provided 
    that the two dates passed are not the same date.If they are the function returns 1. This is to 
    avoid a negative time value being passed in a later lunction call."""
```
Here the lowest number that can be returned by the get day difference function is 1. This is because in the index() function the delay (when an alarm is added to the scheduler) is calculated by finding the difference (in seconds) between the current time and the time on the alarm in a 24 hour period. the amount of seconds in extra days is then calculated by using the days-1 part of the code therefore the lowest that days-1 can be is zero and for that to be the case the lowest number get_day_difference() can return is 1.This is to ensure that a negative value isn't calculated as time can take a negative value.  
```python
def get_coronavirus_data_test() -> str:
    """This function is a test function to show the functionality of the covid API """
```
The get_coronavirus_data_test function is a unit test to check to see if the area code for the whole of the united kingdom is returned by the Cov19API function.If this area code is returned this means that the API query worked and that the area code was returned in the json object produced by the API. 
```python
def get_news_test() -> str:
    """This function is a test function to show the functionality the news API"""
```
The get_news_test function is a unit test to check to see if the status returned by the API is 'ok' if so this means that the news API has been successfully queried as the status of 'ok' was found at its appropriate place in the json object.
```python
def get_weather_test(location: str) -> int:
    """This function begins by taking in a location as a string, which is predefined by the user 
    upon the apps start up.The function then proceeds to read to config file to get an api key .
    This api key is used to get the weather data which is returned in a json format.The required data 
    is then extracted from the json object and returned in a list to be used elsewhere a piece of code"""
```
The get_weather_test function is a unit test to check to see if the status code returned by the API is 200 if so this means that the weather API has been successfully queried as the status code of 200 was found at its appropriate place in the json object.
```python
def interface():
    """This function determines what happens when the user is directed to the / part of the application"""
```
This function determines what happens when the user starts the applicaton. The interface function returns a HTML form which allows the user to input their preferences for a news source and location to recieve weather updates on. 
```python
def index():
    """This function determines what happens when the user is directed to the /index part of the application"""
```
The index function is the main part of the application and handles the populating of the notifications every minute and the setting of alarms.The setting of alarms includes:
- How the program updates the user interface to display the alarm created 
- How the program calcuates the appropriate delay for the alarm 
- How the program handles putting weather and news into the breifing if the user has requested them 
- How the program removes alarms from the interface once they've been triggered
```python
def help():
    """This function determines what happens when the user is directed to the /help part of the application"""
```
The help function displays a help message to the user on how to use the interface when they are directed to the /help part of the application.

Finally the config file is in a json format and should include the following:
- The API keys of the user as strings 
- The string/s used in the covid breifing message 
- The filters used to query the covid19 API and the format you would like them returned in 
- The string/s used in the news breifing message
- The string/s used in weather breifing message
- Any other messages that can be customised or displayed by the user interface 
### Details 
Author: Pierre Siddall
Written in: Python 3.9
Released on: 04/12/2020
licence: CC BY-NC
acknowledgements: Dr Matthew Collison (author of the HTML template used in the index function)
