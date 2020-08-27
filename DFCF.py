from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.chrome.options import Options
import json

def get_data_from_DFCF(stock, x, y):
    DFCF_dict = {'view_num': [], 'comment_num': [], 'title': [], 'poster': [], 'latest_time': [], 'sub_url': []}
    href_list = []
    total_list = []
    print('从第{}页到第{}页'.format(x, y - 1))
    for i in range(x, y):
        print('正在第{}页'.format(i))
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        browser = webdriver.Chrome(options=chrome_options)

        url = 'http://guba.eastmoney.com/list,{}_{}.html'.format(stock, i)
        url2 = 'http://guba.eastmoney.com'
        browser.get(url)
        html_source = browser.page_source
        soup = BeautifulSoup(html_source, "html.parser")
        view_num = soup.find_all('span', class_='l1 a1')
        comment_num = soup.find_all('span', class_='l2 a2')
        title = soup.find_all('span', class_='l3 a3')
        poster = soup.find_all('span', class_='l4 a4')
        time = soup.find_all('span', class_='l5 a5')
        for element in view_num[1:]:
            DFCF_dict['view_num'].append(element.string)
        for element in comment_num[1:]:
            DFCF_dict['comment_num'].append(element.text)
        for element in title[1:]:
            a = element.find('a')
            href = a.get('href')
            title = a.get('title')
            href_list.append(href)
            DFCF_dict['title'].append(title)
        for element in poster[1:]:
            DFCF_dict['poster'].append(element.text)
        for element in time[1:]:
            DFCF_dict['latest_time'].append(element.text)
        for i in range(len(time[1:])):
            if (href_list[i][:5] == '/news') and href_list[i][7].isdigit():
                sub_url = url2 + href_list[i]
            else:
                sub_url = ''
            DFCF_dict['sub_url'].append(sub_url)
        browser.close()
    print('结束爬虫')
    total_list = [DFCF_dict['view_num'], DFCF_dict['comment_num'], DFCF_dict['title'], DFCF_dict['poster'],
                  DFCF_dict['latest_time'], DFCF_dict['sub_url']]
    df = pd.DataFrame(total_list)
    df = df.T
    df.columns = ['view_num', 'comment_num', 'title', 'poster', 'latest_time', 'sub_url']
    return df, DFCF_dict


def get_comment(sub_url):
    comment_list = []
    comment_time_list = []
    sub_comment_list = []
    sub_comment_time_list = []
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    browser = webdriver.Chrome(options=chrome_options)

    browser.get(sub_url)
    html_source = browser.page_source
    soup = BeautifulSoup(html_source, "html.parser")

    post_time = soup.find('div', class_="zwfbtime")
    article = soup.find('div', class_="stockcodec .xeditor").text
    article_like = soup.find_all('div', id='like_wrap')[0].text
    comment = soup.find_all('div', class_='full_text')
    comment_time = soup.find_all('div', class_='publish_time')
    sub_comment = soup.find_all('span', class_="l2_full_text")
    sub_comment_time = soup.find_all('span', class_='time fl')

    page_num = soup.find_all('span', class_='sumpage')
    if len(page_num) == 0:
        page_num = 1
    else:
        page_num = int(page_num[0].text)

    print('本贴共{}页:'.format(page_num))
    for element in comment:
        comment_list.append(element.text)
    for element in comment_time:
        comment_time_list.append(element.text)
    for element in sub_comment:
        sub_comment_list.append(element.text)
    for element in sub_comment_time:
        sub_comment_time_list.append(element.text)
    print('爬取第1页')
    browser.close()

    if page_num > 1:
        for i in range(2, page_num + 1):

            print('爬取第{}页'.format(i))
            new_url = sub_url[:-5] + '_{}'.format(i) + sub_url[-5:]
            browser = webdriver.Chrome(options=chrome_options)
            browser.get(new_url)
            html_source = browser.page_source
            soup = BeautifulSoup(html_source, "html.parser")

            comment = soup.find_all('div', class_='full_text')
            comment_time = soup.find_all('div', class_='publish_time')[4:]
            sub_comment = soup.find_all('span', class_="l2_full_text")
            sub_comment_time = soup.find_all('span', class_='time fl')[4:]

            for element in comment:
                comment_list.append(element.text)
            for element in comment_time:
                comment_time_list.append(element.text)
            for element in sub_comment:
                sub_comment_list.append(element.text)
            for element in sub_comment_time:
                sub_comment_time_list.append(element.text)

            browser.close()
    return article, article_like, comment_list, comment_time_list, sub_comment_list, sub_comment_time_list

if __name__ == '__main__':

    df,DFCF_dict = get_data_from_DFCF(600000,2,3)
    for url in DFCF_dict['sub_url']:
        if url != '':
            article,article_like,comment_list,comment_time_list,sub_comment_list,sub_comment_time_list = get_comment(url)

            DFCF_dict['article'].append(article)
            DFCF_dict['article_like'].append(article_like)
            DFCF_dict['comment'].append(comment_list)
            DFCF_dict['comment_time'].append(comment_time_list)
            DFCF_dict['sub_comment'].append(sub_comment_list)
            DFCF_dict['sub_comment_time'].append(sub_comment_time_list)


    DFCF_json = json.dumps(DFCF_dict,sort_keys=False, indent=4, separators=(',', ': '))
    print(type(DFCF_json))
    f = open('东方财富.json', 'w')
    f.write(DFCF_json)