import requests as req
import os

top10000_eng_long = req.get('https://raw.githubusercontent.com/first20hours/google-10000-english/master/google-10000-english-usa-no-swears-long.txt')
with open('assets/vocabs/top10000_english_long.txt', 'w') as voc_file:
    voc_file.write(top10000_eng_long.text)

top1000_eng = req.get('https://gist.githubusercontent.com/deekayen/4148741/raw/98d35708fa344717d8eee15d11987de6c8e26d7d/1-1000.txt')
with open('assets/vocabs/top1000_english.txt', 'w') as voc_file:
    voc_file.write(top1000_eng.text)

try:
    os.makedirs('stats')
except FileExistsError:
    pass

open('stats/stats.csv', 'a').close()
