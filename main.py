import bs4
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.parse import urlencode
import json
from datetime import datetime, timedelta


def get_news_data(search_term, data_filter, number_of_data):
    # Search through Google News with the "search_term" and get the headlines 
    # and the contents of the news that was released today, this week, this month, 
    # or this year ("date_filter"). Maximum number of headlines is set to 
    # be "number_of_data" or all available news in Google News. 
    # 
    # Parameters: 
    #   search_term  -  a string that will be used by the function to search the news in Google News 
    #                   e.g. 'Samsung Galaxy Note 9', 'Basketball' 
    #   date_filter  -  date that will filter available news 
    #                   `today' - get headlines of the news that are released only in today 
    #                   `this_week' - get headlines of the news that are released in this week 
    #                   `this month' - news released in this month 
    #                   `this_year' - news released in this year
    #   number_of_data - number of headlines

    news_url = "https://news.google.com/rss/search?" + urlencode({
            'q':search_term, 'hl':'en-US', 'gl':'US', 'ceid':'US:en'
            })

    today_datetime = datetime.today()
    last_datetime = today_datetime - timedelta(days=7)

    #today_date = today_datetime.strftime('%Y-%m-%d')
    this_year = today_datetime.strftime('%Y')
    this_month = today_datetime.strftime('%m')
    

    client = urlopen(news_url)
    xml_page = client.read()
    client.close()

    soup_page = BeautifulSoup(xml_page,"xml")
    news_list = soup_page.findAll("item")
    
    if len(news_list) == 0:
        return json.dumps({
                'total_result': '0',
                'search_results': 'The term you entered is not available'
                })
    
    
    # get news title, url and publish date
    search_results = []
    for num, news in enumerate(news_list, start=1):
        if len(search_results) >= number_of_data:
            break

        pub_datetime = datetime.strptime(str(news.pubDate.string), '%a, %d %b %Y %H:%M:%S %Z')
        
        if data_filter == 'today':
            diff_datetime = today_datetime - pub_datetime
            if diff_datetime.days != 0:
                continue
        elif data_filter == 'this_week':
            if pub_datetime <= last_datetime or pub_datetime >= today_datetime:
                continue
        elif data_filter == 'this_month':
            if pub_datetime.strftime('%m') != this_month:
                continue
        elif data_filter == 'this_year':
            if pub_datetime.strftime('%Y') != this_year:
                continue

        news_dict = {}
        news_dict['published_on'] = news.pubDate.string
        news_dict['healines'] = news.title.string
        news_dict['article_url'] = news.link.string
        
        news_dict['source'] = news.source.string
        
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
            'search_results': search_results
            }, indent=4, sort_keys=True)



if __name__ == "__main__":
    print(get_news_data(search_term="UK", data_filter="today", number_of_data=5))

