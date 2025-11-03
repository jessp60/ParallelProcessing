# environment ~/Documents/GitHub/ParallelProcessing/.venv/bin/python
from requests_html import HTML, HTMLSession 
from thread import thread
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

session = HTMLSession()

def scrape_page(title):
    url = f"https://en.wikipedia.org/wiki/Wikipedia:Contents/{title}"
    try:
        response = session.get(url)
        threadOverview = response.html.find("h2") #get all the <h2> elements
        if threadOverview:
            print(f"\nPage title: {title}")
            result = [f"\nPage title: {title}"]
            threadOverview = response.html.find("div.contentsPage__intro p", first = True)
            if threadOverview: 
                print("Description:", threadOverview.text)
            return "\n".join(result)
        else:
            return f"\nPage title: {title}\nNo items found on page."
    except Exception as e:
        return f"\nPage title: {title}\nError occurred: {e}"

def main():
    r = session.get('https://en.wikipedia.org/wiki/Wikipedia:Contents') # response object 
    titles = r.html.find('h3')
    # threadNum = 0 
    titles = [titles[i].text for i in range(0, 13)]
    
    multiP = input("Please select the scraping method (Baseline, Forking, MultiThreading): ")
    startTime = time.perf_counter() 

    match multiP: 
        case "Baseline": 
            print("Baseline Threading")
            for title in titles:
                scrape_page(title)
        case "MultiThreading": 
            # Scrape page using threads 
            with ThreadPoolExecutor(max_workers=13) as executor:
                [executor.submit(scrape_page, title) for title in titles]
        case "Forking": 
        # Scrape page using forks
            pass
        case _: 
            print("Not a valid choice!")
    endTime = time.perf_counter() 
    
    print(f"\nTotal {multiP} Processing Time: ", round(endTime-startTime, 3))

if __name__ == "__main__":
    main()