# environment ~/Documents/GitHub/ParallelProcessing/.venv/bin/python
from requests_html import HTML, HTMLSession 
from thread import thread

# pass contents of file into HTML class 
# with open('simple.html') as html_file: 
#     source = html_file.read()
#     html = HTML(html=source) # instance of HTML object 

session = HTMLSession()
r = session.get('https://en.wikipedia.org/wiki/Wikipedia:Contents') # response object 


titles = r.html.find('h3')
threadNum = 0 
for title in titles:
    threadURL = f"https://en.wikipedia.org/wiki/Wikipedia:Contents/{title.text}"
    print(f"\nPage Title: {title.text}")
    thread = session.get(threadURL)
    threadOverview = thread.html.find("h2")
    if threadOverview: 
        print("Items on page:")
        for overview in threadOverview: 
            print("-", overview.text) 