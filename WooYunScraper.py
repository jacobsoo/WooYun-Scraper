# -*- coding: utf-8 -*-
import re,os,sys
from bs4 import BeautifulSoup
import urllib, argparse
import codecs

def WooYunScraper():
    parser = argparse.ArgumentParser(description='This is a simple WooYun.org scraper.')
    parser.add_argument('-o','--output',help='-o <output_filename>', required=True)
    args = parser.parse_args()
    
    base_url = "http://www.wooyun.org/bugs/new_public/page/"
    scan = base_url + '1'
    resp = urllib.urlopen(scan).read()
    
    found = re.findall('条记录, (.*?) 页', resp, re.DOTALL|re.UNICODE)
    _number_pages = int(found[0])
    
    for i in range(1, _number_pages+1):
        resp2 = urllib.urlopen(base_url + str(i)).read()
        soup = BeautifulSoup(resp2, "html.parser")
        tables = soup.findChildren('table')
        
        hFile = codecs.open(args.output, 'ab', encoding='utf-8')
        my_table = tables[0]
        
        rows = my_table.findAll('tr')
        for tr in rows:
            cols = tr.findAll(['td', 'th'])
            if len(cols) >= 4 and u"提交日期" in cols[0].text:
                pass
            else:
                date = cols[0].string
                hFile.write(u"提交日期 : %s\n" % date)
                title = cols[1].text
                hFile.write(u"漏洞名称 : %s" % title)
                link = cols[1].find('a').get('href')
                hFile.write(u"Link : http://wooyun.org%s\n" % link)
                author = cols[3].string
                hFile.write(u"作者 : %s\n\n" % author)
                grab_page(link)
        hFile.close()

def grab_page(szURL):
    import requests
    from lxml import html
    import sys
    import urlparse
    
    try:
        szURL = "http://wooyun.org" + szURL
        response = urllib.urlopen(szURL).read()
        response2 = requests.get(szURL)
        
        tmp = './wooyun.org/' + os.path.basename(szURL)
        try:
            os.makedirs(tmp)
        except OSError:
            pass
        os.chdir(tmp)
        
        hIndex = codecs.open('index.html', 'w')
        hIndex.write(response)
        hIndex.close()
        
        parsed_body = html.fromstring(response)
        
        # Grab links to all images
        images = parsed_body.xpath('//img/@src')
        if not images:  
            pass
        else:
            # Convert any relative urls to absolute urls
            images = [urlparse.urljoin(response2.url, url) for url in images]
            
            # Only download first 10
            for url in images[0:10]:  
                r = requests.get(url)
                f = open(os.path.basename(url), 'wb')
                f.write(r.content)
                f.close()
        os.chdir('../../')
    except requests.exceptions.RequestException as e:
        pass

if __name__ == "__main__":
    while True:
        try:
            WooYunScraper()
        except KeyboardInterrupt:
            print('\nPausing...  (Hit ENTER to continue, type quit to exit.)')
            try:
                response = raw_input()
                if response == 'quit':
                    break
                print('Resuming...')
            except KeyboardInterrupt:
                print('Resuming...')
                continue