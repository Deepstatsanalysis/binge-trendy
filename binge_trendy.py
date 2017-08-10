import argparse
import re
import requests
import pandas as pd
import numpy as np
from sklearn import linear_model

parser = argparse.ArgumentParser(description="""Command line utility to
determine which TV show episodes are above the norm for a season as rated by IMDb users
for more informed binge watching""")
parser.add_argument('-url', help="IMDb show URL of interest")
parser.add_argument('-key', help="Text file with OMDB API key", type=argparse.FileType("r"))
parser.add_argument('-s', help="Season of interest")
args = parser.parse_args()

imdbID = [x for x in args.url.split("/") if re.match('tt', x)][0]
api_key = args.key.read().rstrip("\n")

omdb_url = "http://www.omdbapi.com/?i=" + imdbID + "&apikey=" + api_key
omdb_url_req = requests.get(omdb_url)
total_seasons = omdb_url_req.json()['totalSeasons']

season = None
if args.s:
    season = list(args.s)
else:
    season = list(range(1, int(total_seasons) + 1))

summary_list = ["Season", "Episode", "Value", "Name"]
episodes = []
final_df = pd.DataFrame()


for x in season:
    local_season, episode, rating, title = [], [], [], []
    omdb_season_url = "http://www.omdbapi.com/?i=" + imdbID + "&Season=" + str(x) + "&apikey=" + api_key
    omdb_season_url_req = requests.get(omdb_season_url)

    episode.append([float(y['Episode']) for y in omdb_season_url_req.json()['Episodes']])
    rating.append([float(y['imdbRating']) for y in omdb_season_url_req.json()['Episodes']])
    title.append([y['Title'] for y in omdb_season_url_req.json()['Episodes']])
    local_season.append([list(str(x) * len(omdb_season_url_req.json()['Episodes']))])
    df = pd.DataFrame([local_season[0][0], episode[0], rating[0], title[0]])

    df = df.transpose()
    df.columns = summary_list

    df_sorted = df.sort_values(by='Episode')
    x = np.array(df_sorted['Value']).reshape(-1, 1)
    y = np.array(df_sorted['Episode']).reshape(-1, 1)
    reg = linear_model.LinearRegression()
    reg.fit(y, x)

    df_sorted['residual'] = x - reg.predict(y)

    final_df = final_df.append(df_sorted)

df_residuals = final_df.query('residual > 0.0')
print df_residuals[['Season', 'Episode', 'Name']]