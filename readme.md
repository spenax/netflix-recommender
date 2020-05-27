🎥 Netflix Recommender
======================

This is a simple tool that checks out the subreddit r/NetflixBestOf for US movie recommendations. It then takes those recommendations and cross-references Rotten Tomatoes to return rating information.

Here's what you need to do to get this script up and running:
1. Generate OAuth2 tokens to access Reddit's API. [Detailed Instructions](https://github.com/reddit-archive/reddit/wiki/OAuth2)
2. Create a config file based on on your_config.yml and insert your API keys.
3. Run it!

If you want more results, you can set change time_window in the config file to 'week' or 'month'. Theoretically you could use 'year', but you really shouldn't given the number of API requests that would likely generate. I have yet to experience any rate limiting issues, but I can only assume that the Rotten Tomatoes API would stop responding after some time. Officially, Fandango has dropped support for public access to the API. They now has an application process for (official) access to the Rotten Tomatoes API. [More info](https://developer.fandango.com/rotten_tomatoes)

Usage Notes:
------------
The movie/tv series meta data sourced from Reddit occasionally less than perfect:

+ Cross-referencing the title of work between the platforms can be challenging. There are movies with the same (or very similar) titles. Additionally, there are movies that get turned into TV shows and vice-versa.[TV Shows based on Movies](https://en.wikipedia.org/wiki/List_of_television_programs_based_on_films). That's where the year comes into play...

+ Cross-referencing the year of a work between the two platforms can also be tough. For films posted on r/NetflixBestOf, the year that gets provided in reddit post title is often the official release year, but sometimes it instead ends up being the year the film was added to (US) Netflix. For TV series, the provided year could be the start date of the first season or the final date of the last season (or anything in that range). When the script fails to find a perfect match exact match for the year, it tries finding a rough match, +/- 1 year.
