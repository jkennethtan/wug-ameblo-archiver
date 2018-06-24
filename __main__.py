import requests
from bs4 import BeautifulSoup
import sys, os, re

def fetch(pageNum):
    result = []
    url = requests.get('https://ameblo.jp/wakeupgirls/page-{}.html'.format(pageNum)).text
    soup = BeautifulSoup(url, 'html.parser')
    for anchor in soup.findAll(rel='bookmark'):
        entryURL = 'https://ameblo.jp'+anchor.get('href')
        s = BeautifulSoup(requests.get(entryURL).text, 'html.parser')
        for main in s.findAll('article'):
            title = main.get('data-unique-entry-title')
            date = main.time.get('datetime')
            time = main.time.get_text().replace('NEW!', '').split(' ')[1]
            imgs = []
            for img in main.findAll('img'):
                if not img.get('src'): continue
                elif img.get('src').startswith('https://stat.ameba.jp/user_images'):
                    img = img.get('src')
                    img = re.sub('\?.*', '', img)
                    img = re.sub('\/t.*_', '/o', img)
                    imgs.append(img)
            result.append({
                'title': title,
                'date': date,
                'time': time,
                'cont': str(main),
                'imgs': imgs
                })
    return result

pageNum = 1
while True:
    try:
        dir_n = os.path.dirname(os.path.realpath(__file__))
        sys.stdout.write('\rNow at page #'+str(pageNum))
        for x in fetch(pageNum):
            date = x.get('date')
            y, m, d = date.split('-')
            time = x.get('time').replace(':', '.')
            if not os.path.exists(y): os.makedirs(y)
            if not os.path.exists(y+'\\'+date+' '+time): os.makedirs(y+'\\'+date+' '+time)
            for img in x.get('imgs'):
                filename = os.path.basename(img)
                r = requests.get(img, stream=True)
                with open(dir_n+'\\'+y+'\\'+date+' '+time+'\\'+filename, 'wb') as f:
                    for chunk in r:
                        f.write(chunk)
            with open(dir_n+'\\'+y+'\\'+date+' '+time+'\\index.html', 'w', encoding='utf-8') as f:
                f.write(x.get('cont'))
        pageNum += 1
        break
    except:
        err = 'Failed at page #{}'.format(pageNum)
        with open(dir_n+'\\logs.log', 'a+') as f:
            f.write(err+'\n')
        print(' '+err)
        pageNum += 1
        continue
