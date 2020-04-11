#!/usr/bin/env python
# coding: utf-8

import numpy as np
import plotly.express as px
import plotly
import pandas as pd

at_bat = ['field_out','strikeout','single','double','home_run','grounded_into_double_play',
          'force_out','field_error','triple','fielders_choice','double_play','fielders_choice_out',
          'strikeout_double_play','other_out']

hit = ['single','double','home_run','triple']

data = (pd.read_csv('Cincinnati_Reds_2019_savant_data.csv')
            .filter(items = ['game_date','player_name','events'])
            .query('events == events')
            .sort_values('game_date')
            .reset_index(drop = True))

data['game_date'] = pd.to_datetime(data['game_date'])
data['hit'] = [1 if x in hit else 0 for x in data['events']]
data['at_bat'] = [1 if x in at_bat else 0 for x in data['events']]
data['home_run'] = [1 if x == 'home_run' else 0 for x in data['events']]

data = (data
            .groupby(['game_date','player_name'])
            .agg({'hit': 'sum', 'at_bat': 'sum', 'home_run': 'sum'})
            .reset_index())

game_list = []
player_list = []

for day in data['game_date'].unique():
    for player in data['player_name'].unique():
        game_list.append(day)
        player_list.append(player)
        
df = (pd.merge(pd.DataFrame({'Game': game_list, 'Player': player_list}),
               data, how = 'left', left_on = ['Game','Player'], right_on = ['game_date','player_name'])
          .drop(['game_date','player_name'], axis = 1)
          .fillna(0)
          .sort_values(['Game','Player']).reset_index(drop = True))

df['hits_running'] = df.groupby(['Player']).cumsum()['hit']
df['at_bats_running'] = df.groupby(['Player']).cumsum()['at_bat']
df['hrs_running'] = df.groupby(['Player']).cumsum()['home_run']
df['ba'] = df['hits_running'] / df['at_bats_running']
df['Game'] = [str(item.strftime('%b-%d')) for item in df['Game']]
df['Team'] = ['Reds' for item in df['Player']]

df = df.fillna(0)

fig = px.scatter(df, x = 'hrs_running', y = 'hits_running', size = 'ba', animation_frame = 'Game',
                 range_x = [-5, 60], range_y = [-10, 175], template = 'simple_white', size_max = 35, hover_name = 'Player',
                 labels = {'hrs_running': 'Home Runs', 'at_bats_running': 'At-Bats',
                           'ba': 'Batting Average', 'Game': 'Date', 'hits_running': 'Hits'},
                 title = 'Cincinnati Reds Batting Stats by Player in 2019', color = 'Team',
                 color_discrete_map = {'Reds': '#C6011F'})

fig.update_layout(showlegend = False, autosize=False,width=1000,height=750)

plotly.io.write_html(fig, file = "Reds_Batters_2019.html", auto_open = True)

