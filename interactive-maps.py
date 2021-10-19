#!/usr/bin/env python
# coding: utf-8

# |------------------------------------------------------------------
# | # Geospatial Data Exercise
# |------------------------------------------------------------------
# |
# | This is a notebook for the third lesson of the kaggle course
# | ["Geospatial Analysis"](https://www.kaggle.com/learn/geospatial-analysis)
# | prepared by Alexis Cook and Jessica Li. The main goal of the lesson is
# | to get used to __Interactive Maps__. We will learn how to use `folium`
# | with following functions.
# |
# | * Map
# | * Marker
# | * MarkerCluster
# | * Circle (= bubble map)
# | * HeatMaps
# | * Choropleth
# |

# | Here 'interactive' means
# | - zoom in  / zoom out
# | - move (drag the map)
# | - tooltip (information shows up when the pointer is on a marker)
# | - popup (information shows up when a marker is clicked)

# | ## 1. Task
# | Create various plots using functions of `folium`. Describe your observations.

# | ## 2. Data
# | 1. Criminal statistics in Boston
# | 2. Underlying maps of the city of Boston
# | 3. Borders (Shapely Polygon) of the districts of Boston

# | ## 3. Notebook
# |
# | Import packages.

import pandas as pd
import geopandas as gpd

from pathlib import Path
import os
import webbrowser
import zipfile

import plotly.graph_objs as go
import folium
from folium import Choropleth, Circle, Marker
from folium.plugins import HeatMap, MarkerCluster

# -------------------------------------------------------
# | Some housekeeping functions.
# | Later they will go to a module ``../kaggle_geospatial`.


def set_cwd(CWD):
    if Path.cwd() != CWD:
        os.chdir(CWD)

# | If we have not downloaded the course data, get it from Alexis Cook's
# | kaggle public dataset.


def set_data_dir(DATA_DIR, KAGGLE_DIR, GEO_DIR, CWD):
    if not Path(DATA_DIR).exists():
        command = 'kaggle d download ' + KAGGLE_DIR
        os.system(command)
        os.chdir(DATA_DIR)
#        with zipfile.ZipFile('geospatial-learn-course-data', 'r') as zip_ref:
        with zipfile.ZipFile(GEO_DIR, 'r') as zip_ref:
            zip_ref.extractall('.')
        os.chdir(CWD)

# | Some housekeeping stuff. Change `pandas`' options so that we can see
# | whole DataFrame without skipping the lines in the middle.


def show_whole_dataframe(show):
    if show:
        pd.options.display.max_rows = 999
        pd.options.display.max_columns = 99

# | This is to store the folium visualization to an html file, and show it
# | on the local browser.


def embed_map(m, file_name):
    from IPython.display import IFrame
    m.save(file_name)
    return IFrame(file_name, width='100%', height='500px')


def embed_plot(fig, file_name):
    from IPython.display import IFrame
    fig.write_html(file_name)
    return IFrame(file_name, width='100%', height='500px')


def show_on_browser(m, file_name):
    '''
    m   : folium Map object
    Do not miss the trailing '/'
    '''
    m.save(file_name)
    url = 'file://'+file_name
    webbrowser.open(url)


# -------------------------------------------------------
# | Set up some directories.

CWD = '/Users/meg/git6/boston_crime/'
DATA_DIR = '../input/geospatial-learn-course-data/'
KAGGLE_DIR = 'alexisbcook/geospatial-learn-course-data'
GEO_DIR = 'geospatial-learn-course-data'

set_cwd(CWD)
set_data_dir(DATA_DIR, KAGGLE_DIR, GEO_DIR, CWD)
show_whole_dataframe(True)

# -------------------------------------------------------
# | Read criminal statistics in Boston.

crimes_dir = DATA_DIR + 'crimes-in-boston/crimes-in-boston/'
crimes = pd.read_csv(crimes_dir+'crime.csv', encoding='latin-1')

# -------------------------------------------------------
# | Plan for a quick processing.
# |
# | * drop rows where the location information ['Lat', 'Long', 'DISTRICT] is missing.
# | * concentrate on the violent crimes.
# | * take only the recent record (in the year 2018 = last recorded year).
# | * take only the daytime crimes.

# | The meanings of the columns are more or less obvious except 'UCR_PART'.
# | [UCR (Uniform Crime Reporting)](https://en.wikipedia.org/wiki/Uniform_Crime_Reports)
# |
# | * Part I  : 8 serious crimes.
# | * Part II : 21 less commonly reported crimes.
# | * Part III: unclear.
# |
# | [Offense Definitions](https://ucr.fbi.gov/crime-in-the-u.s/2011/crime-in-the-u.s.-2011/offense-definitions)

crimes['UCR_PART'].unique()
crimes.loc[crimes['UCR_PART'] == 'Part One', 'OFFENSE_CODE_GROUP'].unique()
crimes.loc[crimes['UCR_PART'] == 'Part Two', 'OFFENSE_CODE_GROUP'].unique()
crimes.loc[crimes['UCR_PART'] == 'Part Three', 'OFFENSE_CODE_GROUP'].unique()
crimes.loc[crimes['UCR_PART'] == 'Other', 'OFFENSE_CODE_GROUP'].unique()

# | First, drop the rows with missing positional information.

crimes.dropna(subset=['Lat', 'Long', 'DISTRICT'], inplace=True)

# | Let us take all the UCR Part I crimes and some of the UCR Part II crimes, as well.

additional_crime_list = ['Simple Assault', 'Harassment', 'Ballistics',
                         'Arson', 'HOME INVASION', 'Criminal Harassment',
                         'Manslaughter']

violent_crimes = list(crimes.loc[crimes['UCR_PART'] == 'Part One',
                                 'OFFENSE_CODE_GROUP'].unique()) + additional_crime_list

crimes = crimes.loc[crimes['OFFENSE_CODE_GROUP'].isin(violent_crimes), :]

# | Just check if 'YEAR' is not given as string. Okay.

crimes['YEAR'].dtype
crimes = crimes.loc[crimes['YEAR'] >= 2018, :]

# | Daytime crimes.

crimes['HOUR'].dtype
crimes = crimes.loc[(crimes['HOUR'] >= 9) & (crimes['HOUR'] <= 18), :]
crimes.reset_index(drop=True, inplace=True)

print(f'\033[36m{len(crimes)} \033[33mcrimes \
in year \033[36m{crimes["YEAR"].max()}\033[33m in Boston\033[0m')

# -------------------------------------------------------
# | Create a map with markers.
# | Calculate the center of the map that we retrieve.

center = [crimes['Lat'].mean(), crimes['Long'].mean()]
zoom = 14
tiles = 'openstreetmap'

m_1 = folium.Map(location=center, tiles=tiles, zoom_start=zoom)
dump = [Marker([r['Lat'], r['Long']],
               ).add_to(m_1)
        for i, r in crimes.iterrows()]

# # -------------------------------------------------------
# | Show it on the notebook and the browser window.

embed_map(m_1, 'm_1.html')

# --
show_on_browser(m_1, CWD+'m_1b.html')

# -------------------------------------------------------
# | The plot above is too much crowded. Try `MarkerCluster` to aggregate
# | the information.

tiles = 'cartodbpositron'
m_2 = folium.Map(location=center, tiles=tiles, zoom_start=zoom)
mc = MarkerCluster()

dump = [mc.add_child(Marker([r['Lat'], r['Long']]))
        for i, r in crimes.iterrows()]
m_2.add_child(mc)

# -------------------------------------------------------
# | Show it on the notebook and the browser window.

embed_map(m_2, 'm_2.html')

# --
show_on_browser(m_2, CWD+'m_2b.html')

# -------------------------------------------------------
# | The districts near the coast line suffer from the large numbers of
# | violent crimes. These include Back Bay, South Boston, and Dorchester.


# -------------------------------------------------------
# | Try a bubble map to see if there is any difference in
# | the distribution of the crimes before and after the lunch time.

def color_producer(val):
    if val <= 14:
        return 'steelblue'
    else:
        return 'indianred'


tiles = 'openstreetmap'
m_3 = folium.Map(location=center, tiles=tiles, zoom_start=zoom)
dump = [Circle([r['Lat'], r['Long']],
               radius=80,
               color='',
               fill_opacity=0.5,
               fill=True,
               fill_color=color_producer(r['HOUR'])).add_to(m_3)
        for i, r in crimes.iterrows()]

# -------------------------------------------------------
# | Show it on the notebook and the browser window.

embed_map(m_3, 'm_3.html')

# --
show_on_browser(m_3, CWD+'m_3b.html')

# -------------------------------------------------------
# | No obvious correlation is seen before and after the lunch time.

# -------------------------------------------------------
# | We should use HeatMap instead, to look for such
# | a potential correlation.

m_5 = folium.Map(location=center, tiles=tiles, zoom_start=zoom)
HeatMap(data=crimes.loc[crimes['DAY_OF_WEEK'].isin(
    ['Saturday', 'Sunday']), ['Lat', 'Long']],
    radius=10).add_to(m_5)

# -------------------------------------------------------
# | Show it on the notebook and the browser window.

embed_map(m_5, 'm_5.html')

# --
show_on_browser(m_5, CWD+'m_5b.html')

# -------------------------------------------------------
m_6 = folium.Map(location=center, tiles=tiles, zoom_start=zoom)
HeatMap(data=crimes.loc[~crimes['DAY_OF_WEEK'].isin(
    ['Saturday', 'Sunday']), ['Lat', 'Long']],
    radius=10).add_to(m_6)

# -------------------------------------------------------
# | Show it on the notebook and the browser window.

embed_map(m_6, 'm_6.html')

# --
show_on_browser(m_6, CWD+'m_6b.html')

# -------------------------------------------------------
# | During the weekend, the crimes are more concentrated in
# | Back Bay area, while on working days, they are more evenly
# | distributed to the south.

# -------------------------------------------------------
# | We shall practice Choropleth here.

districts_dir = '../input/geospatial-learn-course-data/Police_Districts/Police_Districts/'
districts = gpd.read_file(districts_dir + 'Police_Districts.shp')

# -------------------------------------------------------
# | There are two ways to create Choropleth here.
# |
# | 1. specify `geo_data` by `districts` geometry, and
# | use `crimes` to show the statistics.
# |
# | 2. join the two GeoDataFrames (`districts` and `crimes`) and use it in Choropleth.

# | Let us try 2. here.
# | Here both of the data frames to be merged are GeoDataFrame, but
# | we we merge pd.DataFrame and gpd.GeoDataFrame, make sure
# | gpd.GeoDataFrame is on the left, otherwise the merged data frame
# | will be pd.DataFrame instead of gpd.GeoDataFrame.

# | Check if districts are consistent.
sorted(crimes['DISTRICT'].unique()) == sorted(districts['DISTRICT'].unique())

districts = districts.merge(crimes.groupby('DISTRICT').count()['INCIDENT_NUMBER'],
                            left_on='ID', right_on='DISTRICT')

districts = districts[['DISTRICT', 'INCIDENT_NUMBER', 'geometry']]
districts.set_index('DISTRICT', inplace=True)
districts.sort_values('INCIDENT_NUMBER', ascending=False)

# -------------------------------------------------------
tiles = 'cartodbpositron'
m_7 = folium.Map(location=center, tiles=tiles, zoom_start=zoom)
Choropleth(geo_data=districts.__geo_interface__,
           data=districts['INCIDENT_NUMBER'],
           #           key_on='feature.properties.DISTRICT',
           key_on='feature.id',
           fill_color='YlGnBu',
           legend_name="Number of Violent Crimes in Boston (Jan-Aug 2018)").add_to(m_7)

# -------------------------------------------------------
# | Show it on the notebook and the browser window.

embed_map(m_7, 'm_7.html')

# --
show_on_browser(m_7, CWD+'m_7b.html')

# -------------------------------------------------------
# | Use `plotly` to see the incident number of each district.
# |

trace = go.Bar(y=districts.sort_values('INCIDENT_NUMBER').index,
               x=districts.sort_values('INCIDENT_NUMBER')['INCIDENT_NUMBER'],
               orientation='h')

data = [trace]

layout = go.Layout(height=512, width=1024,
                   font=dict(size=20),
                   xaxis=dict(title=dict(
                       text='Number of Violent Crimes in Boston (Jan-Aug 2018)')))

fig = go.Figure(data=data, layout=layout)

# -------------------------------------------------------
# | Show it on the notebook and the browser window.
embed_plot(fig, 'p_1.html')

# --
fig.show()

# -------------------------------------------------------
# | ## 4. Conclusion
# | 1. In terms of the total number of crimes, the district D4 is the worst.
# |
# | 2. On the weekend, the crimes happen more often in D4, while
# | on the working days the incidences are more evenly distributed in D4, B2, and A1.
# |
