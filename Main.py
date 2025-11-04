# environment ~/Documents/GitHub/ParallelProcessing/.venv/bin/python
from requests_html import HTML, HTMLSession 
from thread import thread
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from tkinter import *

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
    pass

def run_scraper():
    print("GUI is working")

# GUI
root = Tk()
root.title("Parallel Processing") #window title
root.config(bg="#572a3b")
root.geometry("620x620")

methods = ["Baseline", "MultiThreading", "Forking"] #different scraping methods
opt = StringVar(root)
opt.set(methods[0]) #default value

titleLabel = Label(root, text="Parallel Processing Scraper", bg="#572a3b", fg="white", font=("Times New Roman", 22, "bold"))
titleLabel.pack(pady=10)

frame = Frame(root, width=620, height=620)
frame.pack(padx=10, pady=10)
frame.pack_propagate(False)

promptLabel = Label(frame, text="Select a scraping method:", font=("Times New Roman", 14))
promptLabel.pack(pady=20)

OptionMenu(frame, opt, *methods).pack(pady=10)

runScraper = Button(frame, text="Run Scraper", command=run_scraper)
runScraper.pack(pady=20)


#table to display results
# lst = [['Method', 'Time (seconds)'],
#        ['Baseline', '0.123'],
#        ['MultiThreading', '0.045'],
#        ['Forking', '0.067']]
# total_rows = len(lst)
# total_columns = len(lst[0])

# table_frame = Frame(frame, bg="#572a3b")
# table_frame.pack(pady=10)

# class Table:
#     def __init__(self, frame):
#         for i in range(total_rows):
#             for j in range(total_columns):
#                 cell = Label(frame, text=lst[i][j], width=20, font=('Arial', 14), bg='#d3d3d3', fg='black', borderwidth=1, relief='solid')
#                 cell.grid(row=i, column=j, padx=1, pady=1)
# t = Table(table_frame)

root.mainloop()