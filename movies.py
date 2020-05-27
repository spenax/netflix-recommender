import praw
import datetime
import re
import requests
import json
import time
import urllib
import yaml
from blessings import Terminal

#Set time range
TIME_WINDOW = "week"

term = Terminal()

with open('config.yml') as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

REDDIT_CLIENT_ID=cfg["reddit"]["client_id"]
REDDIT_CLIENT_SECRET=cfg["reddit"]["client_secret"]
REDDIT_USER_AGENT=cfg["reddit"]["user_agent"]
TIME_WINDOW = cfg["reddit"]["time_window"]

rt_url_base = 'https://www.rottentomatoes.com/api/private/v1.0/'
headers = {'Content-Type': 'application/json'}

reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID,
                    client_secret=REDDIT_CLIENT_SECRET,
                    user_agent=REDDIT_USER_AGENT)

#For comparison https://www.rottentomatoes.com/api/private/v1.0/search?q=cats

class movies:
    def __init__(self, title, year, synop, score, rt_score):
        self.title = title
        self.year = year
        self.synop = synop
        self.score = score
        self.rt_score = rt_score

allMovies = []
submissions = reddit.subreddit('NetflixBestOf').search("[US] -title:[REQUEST]", time_filter=TIME_WINDOW)
for submission in submissions:
    postTitle = submission.title
    score = submission.score
    date_utc = submission.created_utc
    date = datetime.datetime.fromtimestamp(date_utc)

    # Hot fix: using regex because of Issues with search negative queries in search
    if re.search(r'\[REQUEST\]', postTitle) is None:
        movieYearSearch = re.search(r'(?<=\()(1?2?\d{3})(?=\))', postTitle)
    movieNameSearch = re.search(r'(?<=\]\s)(.*)(?=\(1?2?\d\d)', postTitle)
    movieDescSearch = re.search(r'(?<=\(\d{4}\)[^A-Za-z])(.*)', postTitle)
    rt_score = -1

    if not movieYearSearch is None:
        movieYear = movieYearSearch.group(0)
    if not movieNameSearch is None:
        movieName = movieNameSearch.group(0)[:-1]
    else:
        movieName = ""
    if not movieDescSearch is None:
        movieDesc = movieDescSearch.group(0)
    else:
        movieDesc = ""


    #to do: improve handling for this
    if not movieName == "":
        allMovies.append( movies(movieName, movieYear, movieDesc, score, rt_score) )



def find_score(title, year):
    safe_title = urllib.parse.quote(title, safe='')
    api_url = '{rt_url_base}search?q={title}'.format(rt_url_base=rt_url_base, title=safe_title)
    response = requests.get(api_url)
    json_data = json.loads(response.text)

    movie_results = json_data["movies"]
    tv_results = json_data["tvSeries"]
    matched_score=-1

    #try release year supplied from reddit
    if json_data["movieCount"] > 0:
        e = 'Searching for {title} ({year}) in Movies'.format(title=title, year=year)
        print(e)

        for result in movie_results:
            result_year = result['year'] if 'year' in result else 0
            if int(result_year) == int(year) and 'meterScore' in result:
                matched_score += result["meterScore"] + 1
    else:
        e = 'Searching for {title} ({year}) in TV Shows'.format(title=title, year=year)
        print(e)

    if json_data["tvCount"] > 0:

        for result in tv_results:
            startYear = result["startYear"] if 'startYear' in result else 0
            endYear = result["endYear"] if 'endYear' in result else 0

            if int(startYear) == int(year) and 'meterValue' in result:
                matched_score += result["meterValue"] + 1
            if int(endYear) == int(year) and 'meterValue' in result:
                matched_score += result["meterValue"] + 1

    # (Fuzzy search) One last attempt using reddit-supplied year +/- 1 year
    if matched_score < 0:
        prior_year = int(year) - 1
        next_year = int(year) + 1

        if json_data["movieCount"] > 0:
            e = '...now trying a rough search in Movies between {prior_year} and {next_year}'.format(title=title, prior_year=prior_year, next_year=next_year)
            print(e)

            for result in movie_results:
                result_year = result['year'] if 'year' in result else 0
                if abs(int(result_year) - int(year)) < 2 and 'meterScore' in result:
                    matched_score += result["meterScore"] + 1
        else:
            e = '...now trying a rough search in TV Shows between {prior_year} and {next_year}'.format(title=title, prior_year=prior_year, next_year=next_year)
            print(e)

        if json_data["tvCount"] > 0:

            for result in tv_results:
                startYear = result["startYear"] if 'startYear' in result else 0
                endYear = result["endYear"] if 'endYear' in result else 0

                if abs(int(startYear) - int(year)) < 2 and 'meterValue' in result:
                    matched_score += result["meterValue"] + 1
                if abs(int(endYear) - int(year)) < 2 and 'meterValue' in result:
                    matched_score += result["meterValue"] + 1

    # return result
    if matched_score > 60:
        return '🍅 {matched_score}'.format(matched_score=matched_score)

    elif matched_score >= 0:
        return '💩 {matched_score}'.format(matched_score=matched_score)
    else:
        return 'Could not find a score for {title} ({year})'.format(title=title,year=year)


for movie in allMovies:
    print("\n" + term.black_on_white + term.bold + movie.title + term.normal)
    #print(movie.year)
    rotten_score = find_score(movie.title, movie.year)
    #movie.rt_score = rotten_score
    print(rotten_score)
    time.sleep(2)
