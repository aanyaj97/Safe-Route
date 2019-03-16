import requests
import bs4

#The following two functions are from util.py in PA2
def get_request(url):
    '''
    Open a connection to the specified URL and if successful
    read the data.

    Inputs:
        url: must be an absolute URL

    Outputs:
        request object or None

    Examples:
        get_request("http://www.cs.uchicago.edu")
    '''

    #modified; only accepts absolute urls 
    try:
        r = requests.get(url)
        if r.status_code == 404 or r.status_code == 403:
            r = None
    except Exception:
        # fail on any kind of error
        r = None
    return r


def read_request(request):
    '''
    Return data from request object.  Returns result or "" if the read
    fails..
    '''

    try:
        return request.text.encode('iso-8859-1')
    except Exception:
        print("read failed: " + request.url)
        return ""

#From PA2
def url_to_html(url):
    '''
    Attempts to get and read url request for given url
    Inputs:
        url: string
    Outputs:
        Tuple of associated url (string) and html (string)
    '''
    
    req = get_request(url)
    if req is None:
        return None
    html = read_request(req)
    if html is None:
        return None
    return html


def get_current_weather():
    '''
    Retrieves most recent weather from Midway Airport.
    Inputs:
        None 
    Outputs:
        Tuple of (Temperature, Precipitation)
    '''
    
    html = url_to_html('https://w1.weather.gov/data/obhistory/KMDW.html')
    soup = bs4.BeautifulSoup(html, "html5lib")
    table_tags = soup.find_all('table')
    table = table_tags[3]
    row = table.find_all('tr')[3]
    row_tags = row.find_all('td')
    temp = float(str(row_tags[6]).replace('<td>', '').replace('</td>', ''))
    precip = str(row_tags[-1]).replace('<td>', '').replace('</td>', '')
    if precip == '':
        precip = 0
    else: 
        precip = float(precip)
    return temp, precip

