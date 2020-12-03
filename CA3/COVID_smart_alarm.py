######## module init ###############
import time
import sched
import requests
import json
import pyttsx3
import logging
import datetime
from uk_covid19 import Cov19API
from flask import Flask, request, render_template

###### object init ###########
scheduler = sched.scheduler(time.time, time.sleep)
app = Flask(__name__)

######## DATA STRUCTURES ###########

user_alarms = []
preferences = []
numbers_upto_ten = {'01': '1', '02': '2', '03': '3', '04': '4',
                    '05': '5', '06': '6', '07': '7', '08': '8', '09': '9'}

################## FUNCTIONS #########################


def create_log() -> None:
    """This function configures the log file by determining the format of log messages and initialising the log file """
    FORMAT = '%(levelname)s:%(asctime)s%(message)s'  # This determines the format that will be used inside the log file
    logging.basicConfig(format=FORMAT, filename='pyapp.log',
                        level=logging.DEBUG)


def announcement(text: str) -> None:
    """This function takes in a piece of text as a string then initialises the text to speech engine to say the text passed as a paremeter to the function"""
    engine = pyttsx3.init()  # initilisation of pyttsx3 module
    engine.say(text)
    engine.runAndWait()


def get_weather(location: str) -> list:
    """This function begins by taking in a location as a string, which is predefined by the user 
    upon the apps start up.The function then proceeds to read to config file to get an api key .
    This api key is used to get the weather data which is returned in a json format.The required data 
    is then extracted from the json object and returned in a list to be used elsewhere a piece of code"""
    with open("config.json", "r") as file:
        # The json file is read using the json module
        json_file = json.load(file)
    keys = json_file["API-keys"]
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    api_key = keys["Weather"]
    city_name = location
    # using string concatination a full url is made
    complete_url = base_url+"appid="+api_key+"&q="+city_name
    response = requests.get(complete_url)
    weather_data = response.json()
    location_name = weather_data['name']
    weather = weather_data['weather'][0]['description']
    # The following two variable assingments use the round function to round tempratures to 2 decimal places
    tempreature_celesius = round(int(weather_data['main']['temp'])-273.15, 2)
    feels_tempreture_celesius = round(
        int(weather_data['main']['feels_like'])-273.15, 2)
    hPa_pressure = int(weather_data['main']['pressure'])
    humidity_percentage = int(weather_data['main']['humidity'])

    return [location_name, weather, tempreature_celesius, feels_tempreture_celesius, hPa_pressure, humidity_percentage]


def get_news(*args: str) -> list:
    """Similar to the get_weather() function this function begins by taking in multiple arguments as a string, which is predefined by the user 
    upon the apps start up.The function then proceeds to read to config file to get an api key .
    This api key is used to get current news headlines which are returned in a json format.Then the code 
    goes through all the articles in the json object and appends articles with any of the arguments passed into the get news function to a filtered articles list.
    This list is then returned."""
    with open("config.json", "r") as file:
        json_file = json.load(file)
    keys = json_file["API-keys"]
    base_url = "https://newsapi.org/v2/top-headlines?"
    api_key = keys["News"]
    country = "gb"
    complete_url = base_url + "country=" + country + "&apiKey=" + \
        api_key  # Here string concatination is used to form a full url
    # An API call is made to the full url created in the line above using the GET method
    response = requests.get(complete_url)
    json_line = response.json()
    articles = json_line['articles']
    filtered_articles = []
    for article in articles:
        for arg in args:  # Here a for loop is used to check to see if any arguments that were passed into the function are in the current article being checked
            if arg in article['title']:
                filtered_articles.append(article['title'])
    return filtered_articles


def get_coronavirus_data() -> list:
    """This function begins by using the config file to get the filters it needs to pass to Cov19API.The function then queries the goverment 
    covid19 api with the appropriate filters returning them as a json object.The relevant pieces of information are then extracted from the json 
    object and are returned in a list"""
    with open("config.json", "r") as file:
        json_file = json.load(file)
    # Here use of the config file is made to hide the filters used to gather data from the covid API
    cases_and_deaths = json_file['covid-data-filters']['cases_and_deaths']
    overview = ['areaType=overview']
    # using the Cov19API function from the uk_covid19 module a GET request is made to the covid API
    covid_api = Cov19API(filters=overview, structure=cases_and_deaths)
    covid_data = covid_api.get_json()
    date = covid_data['data'][0]['date']
    location = covid_data['data'][0]['name']
    daily_cases = covid_data['data'][0]['cases']['daily']
    cumulative_cases = covid_data['data'][0]['cases']['cumulative']
    daily_deaths = covid_data['data'][0]['deaths']['daily']
    return [date, location, daily_cases, cumulative_cases, daily_deaths]


def breifing(date_time: str, chosen_news: str, chosen_weather: str, hasweather: bool = False, hasnews: bool = False) -> None:
    """This function takes in several parameters which form the briefing messages through data stored in the config file and 
    data returned by the APIs.The function then removes the appropriate alarm from the list of dictionaries and reads out a 
    breifing according to the users preferences when setting the alarm"""
    global user_alarms
    with open("config.json", "r") as file:
        json_file = json.load(file)
    # The following three lines access the config file to retrive the messages that will be used in the breifing
    covid_message = json_file['covid-breifing-strings']
    news_message = json_file['news-briefing-strings']
    weather_message = json_file['weather-breifing-strings']
    # The next three lines all make API calls so that current statistics or predictions can be used as part of the briefing
    covid_data = get_coronavirus_data()
    weather_data = get_weather(chosen_weather)
    news_headlines = get_news(chosen_news)
    covid_string = covid_message['part1'], covid_data[0], covid_message['part2'], covid_data[2], covid_message[
        'part3'], covid_data[1], covid_message['part4'], covid_data[3], covid_message['part5'], covid_data[4], covid_message['part6']
    weather_string = weather_message['part1'], weather_data[0], weather_message['part2'], weather_data[1], weather_message['part3'], str(
        weather_data[2]), weather_message['part4'], str(weather_data[3]), weather_message['part5'], weather_data[4], weather_message['part6'], weather_data[5], weather_message['part7']
    news_headlines_string = news_message['part1']

    for dictionary in user_alarms:
        if date_time in dictionary.values():  # Here a check is made to see if the date and time of an alarm matches the dictionary that is being checked
            user_alarms.remove(dictionary)

    if hasweather == True and hasnews == True:  # The following if and elif statements check to see if the user has requested news and/or weather updates along with covid updates
        for part in range(len(covid_string)):
            announcement(covid_string[part])
        for part in range(len(weather_string)):
            announcement(weather_string[part])
        announcement(news_headlines_string)
        for headline in news_headlines:
            announcement(headline)

    elif hasweather == True:
        for part in range(len(covid_string)):
            announcement(covid_string[part])
        for part in range(len(weather_string)):
            announcement(weather_string[part])

    elif hasnews == True:
        for part in range(len(covid_string)):
            announcement(covid_string[part])
        announcement(news_headlines_string)
        for headline in news_headlines:
            announcement(headline)
    else:  # Here the default breifing is set where the user only recives a covid breifing if they haven't ticked the news or weather tick box
        for part in range(len(covid_string)):
            announcement(covid_string[part])


def populate_notifications(note_list: list, chosen_news: str) -> None:
    """This function makes API calls to the coronavirus and news API.The function then 
    appends the articles that have been filtered to a notifications list.The function also 
    checks the coronavirus data and adds a notification to the notifications list to indidicate 
    that a  certain threshold (in number of cases) has been passed. Notifications are added 
    to the notifications list in the format of a dictionary"""
    with open("config.json", "r") as file:
        json_file = json.load(file)
    # The following two lines make API calls to the covid and news APIs to obtain real time updates on the number of covid cases and news headlines
    covid_data = get_coronavirus_data()
    news_data = get_news(chosen_news)
    for article in news_data:  # Here the filtered news artcles returned by the get_news() function are added to the notifications list
        note_list.append({'title': 'Headline', 'content': article})
    if int(covid_data[2]) > 10000:  # In the following if and elif statements check the number of cases as returned by the get_coronavirus_data() function to see if certain thresholds have been passed
        note_list.append({'title': 'URGENT CORONAVIRUS UPDATE',
                          'content': json_file['other-messages']['thresholds']['threshold1']})
    elif int(covid_data[2]) > 15000:
        note_list.append({'title': 'URGENT CORONAVIRUS UPDATE',
                          'content': json_file['other-messages']['thresholds']['threshold2']})
    elif int(covid_data[2]) > 20000:
        note_list.append({'title': 'URGENT CORONAVIRUS UPDATE',
                          'content': json_file['other-messages']['thresholds']['threshold3']})
    elif int(covid_data[2]) > 25000:
        note_list.append({'title': 'URGENT CORONAVIRUS UPDATE',
                          'content': json_file['other-messages']['thresholds']['threshold4']})
    elif int(covid_data[2]) > 30000:
        note_list.append({'title': 'URGENT CORONAVIRUS UPDATE',
                          'content': json_file['other-messages']['thresholds']['threshold5']})


def get_right_date_numbers(date: str, dictionary: dict) -> int:
    """This function gets the correct date number that can be used in the program.
    As numbers repsesented by 01-09 break the program there fore this function handles 
    this issue by looking to see if those valuse are in the keys of a dictionary passed into the function 
    if so then the day and/or the month are assinged its correct value"""
    date_minus_time = date[:10]  # This line extracts only the date from the date and time of an alarm
    # The following three line extract the year,month and day of the date
    year = date_minus_time[:4]
    month = date_minus_time[5:7]
    day = date_minus_time[8:]
    # Here the nessesary checks are made to change numbers 01-10 (not including 10) to single digit numbers
    if day in dictionary.keys() and month in dictionary.keys():
        day = dictionary[day]
        month = dictionary[month]
    elif day in dictionary.keys():
        day = dictionary[day]
    elif month in dictionary.keys():
        month = dictionary[month]
    else:
        pass
    return int(year), int(month), int(day)


def get_day_difference(date1: str, date2: str) -> int:
    """This function claclates the diffrence of days inbetween two dates passed as strings provided 
    that the two dates passed are not the same date.If they are the function returns 1. This is to 
    avoid a negative time value being passed in a later lunction call."""
    numbers_upto_ten = {'01': '1', '02': '2', '03': '3', '04': '4',
                        '05': '5', '06': '6', '07': '7', '08': '8', '09': '9'}
    # The following two lines make use of the get_right_date_numbers() function to make sure that the date numbers for both dates can be used with the datetime module
    year1, month1, day1 = get_right_date_numbers(date1, numbers_upto_ten)
    year2, month2, day2 = get_right_date_numbers(date2, numbers_upto_ten)
    # Here two date objects are declared using the date numbers assinged to the variables above
    final_date1 = datetime.date(year1, month1, day1)
    final_date2 = datetime.date(year2, month2, day2)
    delta = final_date2-final_date1  # Here the diffrence between two dates is calulated
    if delta.days == 0:  # This line is to make sure that the lowest number of days that can be returned is 1 as the time delay cant be negative
        return 1
    elif delta.days < 0:
        print("you can't set an alarm on this day as it has already passed")
        return None
    else:
        return delta.days  # delta.days indicates that the diffrence shoulf be returned in days


def get_coronavirus_data_test() -> str:
    """This function is a test function to show the functionality of the covid API """
    with open("config.json", "r") as file:
        json_file = json.load(file)
    cases_and_deaths = json_file['covid-data-filters']['cases_and_deaths']
    overview = ['areaType=overview']
    covid_api = Cov19API(filters=overview, structure=cases_and_deaths)
    covid_data = covid_api.get_json()
    # Here the area code is exctracted as its value stays the same throughout the json object
    area_code = covid_data['data'][0]['code']
    return area_code


def get_news_test() -> str:
    """This function is a test function to show the functionality the news API"""
    with open("config.json", "r") as file:
        json_file = json.load(file)
    keys = json_file["API-keys"]
    base_url = "https://newsapi.org/v2/top-headlines?"
    api_key = keys["News"]
    country = "gb"
    complete_url = base_url + "country=" + country + "&apiKey=" + api_key
    response = requests.get(complete_url)
    json_line = response.json()
    # Here the status code is extacted as it is a value that can be tested against in my tests function to see if that value is 'ok' indicating the success of the API request
    status = json_line['status']
    return status


def get_weather_test(location: str) -> int:
    """This function begins by taking in a location as a string, which is predefined by the user 
    upon the apps start up.The function then proceeds to read to config file to get an api key .
    This api key is used to get the weather data which is returned in a json format.The required data 
    is then extracted from the json object and returned in a list to be used elsewhere a piece of code"""
    with open("config.json", "r") as file:
        json_file = json.load(file)
    keys = json_file["API-keys"]
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    api_key = keys["Weather"]
    city_name = location
    complete_url = base_url+"appid="+api_key+"&q="+city_name
    response = requests.get(complete_url)
    weather_data = response.json()
    # Here the numerical code is extracted to be used in the tests function the value of 200 indicates the success of the API request
    code = weather_data['cod']
    return code


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

############################### APP ################################


@app.route('/')
def interface():
    """This function determines what happens when the user is directed to the / part of the application"""
    create_log()  # Here the log file is opened or created
    try:
        scheduler.run(blocking=False)
        return '<strong> Hello before you use the app some of your preferences need to be taken to give you breifings personalised to your needs <strong>\
                <form action="/index" method="get">\
                <label for="newspaper"> Please enter a news website:</label>\
                <input type="text" name="newspaper">\
                <label for="location"> Please enter your location:</label>\
                <input type="text" name="location">\
                <input type="submit">\
                </form>'
    except:
        logging.waring('An error has occured in the program')
        raise RuntimeError


@app.route('/index')
def index():
    """This function determines what happens when the user is directed to the /index part of the application"""
    try:
        global preferences, numbers_upto_ten
        # Here the scheduler is continually run to see if events have been triggered in the scheduler
        scheduler.run(blocking=False)
        user_notifications = []
        # The following two lines gather the arguments for the location of the user and their news preference
        location = request.args.get('location')
        newspaper = request.args.get('newspaper')

        if location == None or newspaper == None:
            pass
        else:
            preferences.append(newspaper)
            preferences.append(location)

        news_site = preferences[0]
        weather_location = preferences[1]
        # Here the users preferences are passed as arguments to the populate notifications function
        populate_notifications(user_notifications, news_site, weather_location)
        time_hold = time.localtime()
        # Here the function strftime returns the local time in the format HH:MM
        current_time = time.strftime("%H:%M", time_hold)
        # This checks to see if the user has input an alarm
        alarm_time = request.args.get("alarm")
        # This returns the current date and time on the users device
        current_date_time = str(datetime.datetime.today())
        if alarm_time:
            # Here the label of the alarm is extracted
            label = request.args.get('two')
            # An alarm entry is created
            entry = {'title': label, 'content': alarm_time}
            user_alarms.append(entry)
            alarm_time_seconds = (
                int(alarm_time[11:13])*3600)+(int(alarm_time[14:])*60)  # Here the alarm time in seconds is calculated
            current_time_seconds = (
                int(current_time[0:2])*3600)+(int(current_time[3:])*60)  # Here the current time in seconds is calculated
            # Here the get_day_difference() function is used to calculate the diffrence in days between two dates
            days = get_day_difference(current_date_time, alarm_time)
            delay = (abs(alarm_time_seconds-current_time_seconds) +
                     ((days-1)*24*60**2))  # Here the appropriate delay to be used by the scheduler is determined wear it is the number if seconds between the two times in a 24 hour period + the number of seconds in the diffrence in days minus 1
            # The following two lines check to see if the user has requested news and/or weather in their  breifing
            news = request.args.get("news")
            weather = request.args.get("weather")
            if news == "news" and weather == "weather":  # The following if and elif statements check to see what type of briefing the user wanted and schedules an event using the briefing function to give the approriate breifing
                wantsnews = True
                wantsweather = True
                covid_news_and_weather = scheduler.enter(delay, 1, breifing, argument=(
                    alarm_time, news_site, weather_location, wantsweather, wantsnews))
            elif news == "news":
                wantsnews = True
                wantsweather = False
                covid_and_news = scheduler.enter(delay, 1, breifing, argument=(
                    alarm_time, news_site, weather_location, wantsweather, wantsnews))
                pass
            elif weather == "weather":
                wantsnews = False
                wantsweather = True
                covid_and_weather = scheduler.enter(delay, 1, breifing, argument=(
                    alarm_time, news_site, weather_location, wantsweather, wantsnews))
            else:
                wantsnews = False
                wantsweather = False
                only_covid = scheduler.enter(delay, 1, breifing, argument=(
                    alarm_time, news_site, weather_location, wantsweather, wantsnews))

        # Here the HTML template is returned with its appropriate lists of alarms and notifications and sets the title message
        return render_template('template.html', title='Welcome to your daily breifing', alarms=user_alarms, notifications=user_notifications)
    except:
        # Here a warning is put into the log file to indicate something that went wrong during the runtime of the program
        logging.warning('An error has been detected')
        raise RuntimeError


@app.route('/help')
def help():
    """This function determines what happens when the user is directed to the /help part of the application"""
    with open("config.json", "r") as file:
        json_file = json.load(file)
    # Here the config file is read to get the help message that is to be displayed in the help part of the application
    message = json_file['other-messages']['help']
    return message


if __name__ == '__main__':
    app.run()  # Here the app is run continuously
