Netflix Recommender
===================

A simple tool that checks out the subreddit r/NetflixBestOf for US movie recommendations.

It then takes those recommendations and cross references Rotten Tomatoes.

Note: Fandango now has an application process for (official) access to the Rotten Tomatoes API. [More info](https://developer.fandango.com/rotten_tomatoes)

Here's what you need to do to get this script up and running:
[1] Generate OAuth2 tokens to access Reddit's API. [Detailed Instructions](https://github.com/reddit-archive/reddit/wiki/OAuth2)
[2] Create a config file based on on your_config.yml and insert your OAuth2 information.
[3] Run it!

If you want more results you can change the time filter to 'week' or 'month'. (Theoretically you could use 'year', but you really should not given the number of API requests that would generate.)
