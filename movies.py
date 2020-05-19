import praw
import datetime
import re
import requests
import json
import time
import urllib
import yaml

with open('config.yml') as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

reddit_client_id=cfg["reddit"]["client_id"]
reddit_client_secret=cfg["reddit"]["client_secret"]
reddit_user_agent=cfg["reddit"]["user_agent"]


rt_url_base = 'https://www.rottentomatoes.com/api/private/v1.0/'
headers = {'Content-Type': 'application/json'}

reddit = praw.Reddit(client_id=reddit_client_id,
                    client_secret=reddit_client_secret,
                    user_agent=reddit_user_agent)

#For comparison https://www.rottentomatoes.com/api/private/v1.0/search?q=cats

class movies:
    def __init__(self, title, year, synop, score, rt_score):
        self.title = title
        self.year = year
        self.synop = synop
        self.score = score
        self.rt_score = rt_score

allMovies = []
submissions = reddit.subreddit('NetflixBestOf').search("[US] -title:[REQUEST]", time_filter='day')
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
        movieName = movieNameSearch.group(0)
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
    #to do: remove special characters from title query completely?
    safe_title = urllib.parse.quote(title, safe='')
    api_url = '{rt_url_base}search?q={title}'.format(rt_url_base=rt_url_base, title=safe_title)
    response = requests.get(api_url)
    json_data = json.loads(response.text)
    movie_results = json_data["movies"]
    tv_results = json_data["tvSeries"]
    matched_score=-1


    if json_data["movieCount"] > 0:
        e = 'Searching for {title} in Movies'.format(title=title)
        print(e)

        for result in movie_results:
            result_year = result['year'] if 'year' in result else 0
            if int(result_year) == int(year) and 'meterScore' in result:
                matched_score += result["meterScore"] + 1
    else:
        e = 'Searching for {title} in TV Shows'.format(title=title)
        print(e)

    if json_data["tvCount"] > 0:

        for result in tv_results:
            startYear = result["startYear"] if 'startYear' in result else 0
            endYear = result["endYear"] if 'endYear' in result else 0

            if int(startYear) == int(year) and 'meterValue' in result:
                matched_score += result["meterValue"] + 1
            if int(endYear) == int(year) and 'meterValue' in result:
                matched_score += result["meterValue"] + 1
    if matched_score > 60:
        return '🍅 {matched_score}'.format(matched_score=matched_score)

    elif matched_score >= 0:
        return '💩 {matched_score}'.format(matched_score=matched_score)

    else:
        return 'Cound not find score for {title} ({year})'.format(title=title,year=year)


for movie in allMovies:
    rotten_score = find_score(movie.title, movie.year)
    movie.rt_score = rotten_score
    print(movie.title)
    print(movie.year)
    print(movie.rt_score)
    time.sleep(2)
