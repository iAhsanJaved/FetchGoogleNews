import bs4
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.parse import urlencode
import json
from datetime import datetime, timedelta
import time
import calendar
import numbers

def get_news_data(search_term, data_filter=''):
    # Search through Google News with the "search_term" and get the headlines 
    # and the contents of the news that was released today, this week, this month, 
    # or this year ("date_filter"). 
    # 
    # Parameters: 
    #   search_term  -  a string that will be used by the function to search the news in Google News 
    #                   e.g. 'Samsung Galaxy Note 9', 'Basketball' 
    #   date_filter  -  date that will filter available news 
    #                   'today' - get headlines of the news that are released only in today 
    #                   'this_week' - get headlines of the news that are released in this week 
    #                   'this month' - news released in this month 
    #                   'this_year' - news released in this year
    #                    number - news released in number of days ago
   

    today_datetime = datetime.today()
    last_datetime = today_datetime - timedelta(days=7)
    yesterday_datetime = today_datetime - timedelta(days=1)

    today_date = today_datetime.strftime('%Y-%m-%d')
    
    this_year = today_datetime.strftime('%Y')
    this_month = today_datetime.strftime('%m')

    if data_filter == 'today':
        search_term = search_term + ' after:'+yesterday_datetime.strftime('%Y-%m-%d')
    elif data_filter == 'this_week':
        search_term = search_term + ' after:'+last_datetime.strftime('%Y-%m-%d')+' before:'+today_date
    elif data_filter == 'this_month':
        temp_month = int(this_month)-1
        temp_year = int(this_year)
        if temp_month == 0:
            temp_month = 12
            temp_year = temp_year - 1
        search_term = search_term + ' after:'+str(temp_year)+'-'+str(temp_month)+'-'+str(calendar.monthrange(temp_year, temp_month)[1])
    elif data_filter == 'this_year':
        search_term = search_term + ' after:'+ str(int(this_year)-1)
    elif isinstance(data_filter, numbers.Integral):
        last_datetime = today_datetime - timedelta(days=data_filter)
        search_term = search_term + ' after:'+last_datetime.strftime('%Y-%m-%d')+' before:'+today_date


    news_url = "https://news.google.com/rss/search?" + urlencode({
            'q':search_term, 'hl':'en-US', 'gl':'US', 'ceid':'US:en'
            })

    

    client = urlopen(news_url)
    xml_page = client.read()
    client.close()

    soup_page = BeautifulSoup(xml_page,"xml")
    news_list = soup_page.findAll("item")
    
    if len(news_list) == 0:
        return json.dumps({
                'total_result': '0',
                'search_results': 'There is no data about the search term '+search_term
                })
    
    
    # get news title, url and publish date
    search_results = []
    for num, news in enumerate(news_list, start=1):

        news_dict = {}
        news_dict['published_on'] = news.pubDate.string
        news_dict['healines'] = news.title.string
        news_dict['article_url'] = news.link.string
        
        
        # clean description
        temp_desc = str(news.description.get_text())
        desc_soup = BeautifulSoup(temp_desc, 'html.parser')
        # remove title and source in description
        temp_desc = temp_desc.replace(str(desc_soup.a), '', 1)
        temp_desc = temp_desc.replace(str(desc_soup.font), '', 1)
        desc_soup = BeautifulSoup(temp_desc, 'html.parser')
        temp_desc = desc_soup.get_text()

        news_dict['short_description'] = temp_desc.lstrip()
        
        search_results.append(news_dict)

    search_results.sort(key = lambda x: datetime.strptime(x['published_on'], '%a, %d %b %Y %H:%M:%S %Z')) 

    
    return json.dumps({
            'total_result': str(len(search_results)),
            'search_results': {
                'headlines': list(map(lambda d: d['healines'], search_results)),
                'short_descriptions': list(map(lambda d: d['short_description'], search_results)),
                'article_urls': list(map(lambda d: d['article_url'], search_results)),
                'published_on': list(map(lambda d: d['published_on'], search_results))
            }
            }, indent=4, sort_keys=True)



if __name__ == "__main__":
    start = time.time()
    print(get_news_data(search_term="UK", data_filter=5))
    end = time.time()
    print("Execution time", end - start)

