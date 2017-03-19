from bs4 import BeautifulSoup
import requests
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import math

# Define dict
songs = {}

# Billboard hot 100 page
url = "http://www.billboard.com/charts/hot-100"

def get_ranks(url, i):
    global songs
    # Get page
    r = requests.get(url)
    # Cook soup
    soup = BeautifulSoup(r.text, 'html.parser')
    # Extract ranks
    for song in soup.find_all(class_='chart-row__main-display'):
        song_rank   = song.find(class_='chart-row__current-week').string
        song_title  = song.find(class_='chart-row__song').string
        song_artist = song.find(class_='chart-row__artist').string.strip()
        song_name   = song_title + " : " + song_artist
        song_name   = str(song_name)
        if songs.get(song_name, 'hrily') is 'hrily':
            songs[song_name] = [[], []]
        songs[song_name][0].append(i)
        songs[song_name][1].append(int(song_rank))
    return soup

def print_ranks():
    global songs
    for name in songs.keys():
        print name + " = " + str(songs[name])

def get_previous_week_link(soup):
    link = soup.find(title="Previous Week")
    return link['href']

def get_last_n_ranks(n=1):
    global url
    for i in range(n):
        soup = get_ranks(url, n-i)
        url  = "http://www.billboard.com" + get_previous_week_link(soup)

get_last_n_ranks(6)

print_ranks()

# Prediction
def exponential_fit(x, a, b, c):
#     return a*x + b
    return a*x*x + b*x + c
#     return a*np.exp(-b*x) + c

nCorrect = 0
nCompute = 0
difference = 0
mDifference = 0

for name in songs.keys():
    if len(songs[name][0])<4:
        continue
    x = songs[name][0]
    y = songs[name][1]
#     print x, y
    x = x[1:]
    y = y[1:]
#     print x, y
    x = np.array(x)
    y = np.array(y)
    x = x[::-1]
    y = y[::-1]
#     print x, y
    try:
        fitting_parameters, covariance = curve_fit(exponential_fit, x, y)
        a, b, c = fitting_parameters

        next_y_correct = songs[name][1][0]

        next_x = 6
        next_y = exponential_fit(next_x, a, b, c)


        if next_y_correct == math.floor(next_y) or next_y_correct == math.floor(next_y+1):
            nCorrect = nCorrect + 1
        
        print name
        print y, next_y_correct, next_y
        
        nCompute = nCompute + 1
        difference = difference + abs(next_y_correct - next_y)
        if mDifference < abs(next_y_correct - next_y):
            mDifference = abs(next_y_correct - next_y)
    except:
        print "Prediction failed for "+name

print nCorrect, nCompute
print str( (1.0*nCorrect/nCompute)*100.0 ) + "%"
print 1.0*difference/nCompute
print mDifference