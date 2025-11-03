# environment ~/Documents/GitHub/ParallelProcessing/.venv/bin/python
from requests_html import HTML, HTMLSession 
from thread import thread
from concurrent.futures import ThreadPoolExecutor, as_completed

# pass contents of file into HTML class 
# with open('simple.html') as html_file: 
#     source = html_file.read()
#     html = HTML(html=source) # instance of HTML object 

session = HTMLSession()

def scrape_page(title):
    url = f"https://en.wikipedia.org/wiki/Wikipedia:Contents/{title}"
    try:
        response = session.get(url)
        threadOverview = response.html.find("h2") #get all the <h2> elements
        if threadOverview:
            result = [f"\npage title: {title}", "items on page: "]
            for overview in threadOverview:
                result.append(f"- {overview.text}")
            return "\n".join(result)
        else:
            return f"\npage title: {title}\nNo items found on page."
    except Exception as e:
        return f"\npage title: {title}\nError occurred: {e}"

def main():
    r = session.get('https://en.wikipedia.org/wiki/Wikipedia:Contents') # response object 
    titles = r.html.find('h3')
# threadNum = 0 
    subset = [titles[i].text for i in range(0, 13)]
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(scrape_page, title) for title in subset]

        for future in as_completed(futures):
            print(future.result())

if __name__ == "__main__":
    main()

      # Browse by subject
# for i in range(0, 13):  # Browse by subject 
#     pageName = titles[i].text
#     print(f"\nPage Title: {pageName}")
#     thread = session.get(f"https://en.wikipedia.org/wiki/Wikipedia:Contents/{pageName}")
#     threadOverview = thread.html.find("h2")
#     if threadOverview: 
#         print("Items on page:")
#         for overview in threadOverview: 
#             print("-", overview.text) 