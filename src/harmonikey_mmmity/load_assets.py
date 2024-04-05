import requests as req
import os

def download_write_file(filepath: str, url: str):
    out_req = req.get(url)
    with open(filepath, 'w') as voc_file:
        voc_file.write(out_req.text)

def mkdir_if_not_exists(path: str):
    names = path.split('/')
    current_dir = os.getcwd()
    for name in names:
        if not os.path.exists(name):
            os.mkdir(name)
        os.chdir(name)
        print(os.getcwd())
    os.chdir(current_dir)

def load_assets():

    mkdir_if_not_exists('stats')
    mkdir_if_not_exists('assets/vocabs')
    mkdir_if_not_exists('assets/texts')

    download_write_file(
        'assets/vocabs/top10000_english_long.txt',
        'https://raw.githubusercontent.com/first20hours/google-10000-english/master/google-10000-english-usa-no-swears-long.txt'
    )

    download_write_file(
        'assets/vocabs/top1000_english.txt',
        'https://gist.githubusercontent.com/deekayen/4148741/raw/98d35708fa344717d8eee15d11987de6c8e26d7d/1-1000.txt'
    )

    open('stats/stats.csv', 'a').close()
    if os.path.exists('stats/.gitkeep'):
        os.remove('stats/.gitkeep')

    if os.path.exists('assets/vocabs/.gitkeep'):
        os.remove('assets/vocabs/.gitkeep')

if __name__ == '__main__':
    load_assets()
