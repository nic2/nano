import pandas as pd
from ggplot import *

turnstile_weather = pandas.read_csv('turnstile_data_master_with_weather.csv')

plot = ggplot(turnstile_weather, aes(x='Hour', y=turnstile_weather['ENTRIESn_hourly'], color='UNIT')) + \
     geom_point() + ggtitle('NYC subway entries by time of day')