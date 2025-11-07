# environment ~/Documents/GitHub/ParallelProcessing/.venv/bin/python
from requests_html import HTML, HTMLSession 
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from tkinter import *

session = HTMLSession()

#scraper function
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
    
def baseline_scraper():
    r = session.get('https://en.wikipedia.org/wiki/Wikipedia:Contents') # response object
    titles = [t.text for t in r.html.find('h3')[:13]] # get first 13 titles

    startTime = time.perf_counter()
    for title in titles:
        scrape_page(title)
    endTime = time.perf_counter()
    elapsed = round(endTime - startTime, 3)
    print(f"\nTotal Baseline Processing Time: {elapsed} seconds")
    return elapsed

def multithreading_scraper():
    r = session.get('https://en.wikipedia.org/wiki/Wikipedia:Contents') # response object
    titles = [t.text for t in r.html.find('h3')[:13]] # get first 13 titles

    startTime = time.perf_counter()
    with ThreadPoolExecutor(max_workers=13) as executor: 
        futures = [executor.submit(scrape_page, title) for title in titles]
        for future in as_completed(futures):
            future.result()
    endTime = time.perf_counter()
    elapsed = round(endTime - startTime, 3)
    print(f"\nTotal MultiThreading Processing Time: {elapsed} seconds")
    return elapsed

def main():
    # r = session.get('https://en.wikipedia.org/wiki/Wikipedia:Contents') # response object 
    # titles = r.html.find('h3')
    # # threadNum = 0 
    # titles = [titles[i].text for i in range(0, 13)]
    
    # multiP = input("Please select the scraping method (Baseline, Forking, MultiThreading): ")
    # startTime = time.perf_counter() 

    # match multiP: 
    #     case "Baseline": 
    #         print("Baseline Threading")
    #         for title in titles:
    #             scrape_page(title)
    #     case "MultiThreading": 
    #         # Scrape page using threads 
    #         with ThreadPoolExecutor(max_workers=13) as executor:
    #             [executor.submit(scrape_page, title) for title in titles]
    #     case "Forking": 
    #     # Scrape page using forks
    #         pass
    #     case _: 
    #         print("Not a valid choice!")
    # endTime = time.perf_counter() 
    
    # print(f"\nTotal {multiP} Processing Time: ", round(endTime-startTime, 3))
    pass
if __name__ == "__main__":
    pass

#GUI Code
def run_scraper():
    method = opt.get()
    clear_canvas()
    show_diagram(method)
    if method == "Baseline":
        threading.Thread(target=run_baseline_scraper).start()
    elif method == "MultiThreading":
        threading.Thread(target=run_multithreading_scraper).start()
    else: 
        canvas.create_text(300, 180, text=f"{method} method not implemented yet.", font=("Arial", 12), fill="red")  

def run_baseline_scraper():
    time.sleep(0.5)
    elapsed = baseline_scraper()
    show_result(elapsed)

def run_multithreading_scraper():
    time.sleep(0.5)  #simulate delay for UI refresh
    elapsed = multithreading_scraper()
    show_result(elapsed)

#GUI setup
root = Tk()
root.title("Parallel Processing") #window title
root.config(bg="#572a3b")
root.geometry("700x700")

titleLabel = Label(root, text="Parallel Processing Scraper", bg="#572a3b", fg="white", font=("Times New Roman", 22, "bold"))
titleLabel.pack(pady=10)

descLabel = Label (root, text="program that compares different scraping methods (edit this later)", bg="#572a3b", fg="white", font=("Times New Roman", 14), justify="center")
descLabel.pack(pady= 5)

#main frame
frame = Frame(root, bg="white", bd=2, relief="groove")
frame.pack(fill = "both", expand=True, padx=20, pady=(5, 0))

#dropdown menu
methods = ["Baseline", "MultiThreading", "Forking"] #different scraping methods
opt = StringVar(root)
opt.set(methods[0]) #default value

promptLabel = Label(frame, text="Select a scraping method:", font=("Times New Roman", 14))
promptLabel.pack(pady=20)

OptionMenu(frame, opt, *methods).pack(pady=10)

runScraper = Button(frame, text="Run Scraper", command=run_scraper)
runScraper.pack(pady=20)

#diagram drawings (using canvas)
canvas = Canvas(frame, width = 600, height = 260, bg="white")
canvas.pack(pady=10)

def clear_canvas():
    canvas.delete("all")

# diagram display for each method
def show_diagram(method):
    clear_canvas()
    if method == "Baseline":
        canvas.create_text(300, 20, text="baseline diagram", font = ("Arial", 16, "bold"))
        canvas.create_text(300, 40, text="baseline def/description....", font=("Arial", 10))
        
        for i, color in enumerate(["#a9a9a9", "#8b8b8b", "#696969","#484848", "#303030"]):
            x = 50 + i *100
            canvas.create_rectangle(x, 80, x+80, 120, fill=color, outline="")
            canvas.create_text(x+40, 150, text=f"Thread {i+1}", font=("Arial", 10))
    elif method == "MultiThreading":
        canvas.create_text(300, 20, text="multi-threading diagram", font = ("Arial", 16, "bold"))
        canvas.create_text(300, 40, text="multithreading def/description....", font=("Arial", 10))
        
        for i, color in enumerate(["#696969", "#696969", "#696969","#696969", "#696969"]):
            y = 60 + i *25
            canvas.create_rectangle(80, y, 520, y+20, fill=color, outline="")
            canvas.create_text(300, y+10, text=f"Thread {i+1}", font=("Arial", 10))
    elif method == "Forking":
        pass

#display the result
def show_result(time_value):
    canvas.create_text(300, 210, text=f"Total Time: {time_value} seconds", font=("Arial", 12), fill="green")


#footer
footerFrame = Frame(root, bg="#572a3b")
footerFrame.pack(fill="x", side="bottom")
footer = Label(footerFrame, 
               text="CS4310 - Fall 2025 | Parallel Processing Project", 
               bg = "#572a3b", fg="white", font=("Times New Roman", 14))
footerNames = Label(footerFrame, text = "Arin Boyadjian, Jessica Pinto, Kaitlin Yen", bg="#572a3b", fg="white", font=("Times New Roman", 12))
footer.pack(pady=5)
footerNames.pack(pady=(0,5))

#table to display results
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
