# import the needed libraries
import requests
import pandas as pd
import time # for timing script
import xml.etree.ElementTree as ET # built in library

def clean_url(searched_item,data_filter=''):
    """
    OUTPUT : url to be fecthed for the searched_item and data_filter
     ---------------------------------------------------
    Parameters: 
      today' - get headlines of the news that are released only in today 
                       'this_week' - get headlines of the news that are released in this week 
                       'this month' - news released in this month 
                       'this_year' - news released in this year
                        number : int/str input for number of days ago
                        or '' blank to get all data
    """
    x =pd.datetime.today()
    today =str(x)[:10]
    yesterday = str(x + pd.Timedelta(days=-1))[:10]
    this_week = str(x + pd.Timedelta(days=-7))[:10]
    if data_filter == 'today':
        time = 'after' + yesterday
    elif data_filter == 'this_week':
        time = 'after'+ this_week + '+before' + today
    elif data_filter == 'this_year':
        time = 'after'+str(x.year -1)
    elif str(data_filter).isdigit():
        temp_time = str(x + pd.Timedelta(days=-int(data_filter)))[:10]
        time =  'after'+ temp_time + 'before' + today
    else:
        time=''
    url = 'https://news.google.com/rss/search?q=uk+'+time+'&hl=en-US&gl=US&ceid=US%3Aen'
    return url

# clear the description
def get_text(x):
    start = x.find('<p>')+3
    end = x.find('</p>')
    return x[start:end]

def get_news(search_term, data_filter=''):
    """
    Search through Google News with the "search_term" and get the headlines 
     and the contents of the news that was released today, this week, this month, 
    or this year ("date_filter"). 
    """
    
    url = get_url(search_term, data_filter='')
    response = requests.get(url)
    # get the root directly as we have text file of string now
    root= ET.fromstring(response.text)
    #get the required data
    title = [i.text for i in root.findall('.//channel/item/title') ]
    link = [i.text for i in root.findall('.//channel/item/link') ]
    description = [i.text for i in root.findall('.//channel/item/description') ]
    pubDate = [i.text for i in root.findall('.//channel/item/pubDate') ]
    source = [i.text for i in root.findall('.//channel/item/source') ]
    # clear the description
    short_description = list(map(get_text,description))
    
    # set the data frame
    df = pd.DataFrame({'title':title, 'link':link, 'description':short_description,'date':pubDate,'source':source })
    # adjust the date column
    df.date = pd.to_datetime(df.date, unit='ns')
    # for saving purpose uncomment the below
    df.to_csv(f'{search_term}_news.csv', encoding='utf-8-sig' , index=False)
    return df

if __name__ == "__main__":
    start = time.time()
    search_term = str(input('Enter your search term here: '))
    data = get_news(search_term, data_filter='5')
    end = time.time()-start
    print("Execution time", end)