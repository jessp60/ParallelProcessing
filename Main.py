# environment ~/Documents/GitHub/ParallelProcessing/.venv/bin/python
from requests_html import HTML, HTMLSession 
from multiprocessing import Process, Queue
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from tkinter import *

session = HTMLSession()

#scraper function
def scrape_page(title, queue=None):
    url = f"https://en.wikipedia.org/wiki/Wikipedia:Contents/{title}"
    try:
        response = session.get(url)
        threadOverview = response.html.find("h2") #get all the <h2> elements
        if threadOverview:
            #print(f"\nPage title: {title}")
            result_text = f"\nPage title: {title}"
            threadOverview = response.html.find("div.contentsPage__intro p", first = True)
            if threadOverview: 
                result_text += f"\nDescription: {threadOverview.text}\n"
            else:
                result_text += "\nNo description found.\n"
        else:
            result_text = f"\nPage title: {title}\nNo items found on page."

        #queue for forking (if we are not using queue, send the results back to the main process)
        if queue is not None:
            queue.put(result_text)
            
    except Exception as e:
        return f"\nPage title: {title}\nError occurred: {e}"
    
    # print in result box
    #print(result_text)
    root.after(0, lambda:(
        result_box.insert(END, result_text + "\n"),
        result_box.see(END)
    ))
    
    return result_text

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
    threads = []
    for title in titles:
        t = threading.Thread(target=scrape_page, args=(title,))
        t.start()
        threads.append(t)

    for index, t in enumerate(threads):
        t.join()
        print(f"Thread {index} completed.")

    endTime = time.perf_counter()
    elapsed = round(endTime - startTime, 3)
    print(f"\nTotal MultiThreading Processing Time: {elapsed} seconds")
    return elapsed

def forking_scraper():
    r = session.get('https://en.wikipedia.org/wiki/Wikipedia:Contents') # response object
    titles = [t.text for t in r.html.find('h3')[:13]] # get first 13 titles

    queue = Queue() #to get the resuls back from the child processes

    startTime = time.perf_counter()
    processes = []
    for title in titles:
        p = Process(target=scrape_page, args=(title,queue))
        p.start()
        processes.append(p)

    for index, p in enumerate(processes):
        p.join()
        print(f"Process {index} completed.")

    endTime = time.perf_counter()
    elapsed = round(endTime - startTime, 3)

    results = []
    while not queue.empty():
        results.append(queue.get())

    print(f"\nTotal Forking Processing Time: {elapsed} seconds")
    return elapsed, results

#GUI Code
def run_scraper():
    method = opt.get()
    clear_canvas()
    result_box.delete(1.0, END)  #clear previous results
    show_diagram(method)
    if method == "Baseline":
        threading.Thread(target=run_baseline_scraper).start()
    elif method == "MultiThreading":
        threading.Thread(target=run_multithreading_scraper).start()
    else:
        threading.Thread(target=run_forking_scraper).start() 

    selected_website = website_opt.get()
    if selected_website == "Wikipedia":
        pass
    else:
        pass

def run_baseline_scraper():
    time.sleep(0.5)
    elapsed = baseline_scraper()
    root.after(0, lambda: (
        canvas.delete("status_text"), #remove processing text
        show_result(elapsed)
    ))

def run_multithreading_scraper():
    time.sleep(0.5)  #simulate delay for UI refresh
    elapsed = multithreading_scraper()
    root.after(0, lambda: (
        canvas.delete("status_text"), #remove processing text
        show_result(elapsed)
    ))

def run_forking_scraper():
    time.sleep(0.5)  #simulate delay for UI refresh
    elapsed, results = forking_scraper()

    def update_gui():
        result_box.delete(1.0, END)
        for r in results:
            result_box.insert(END, r +"\n")
        result_box.see(END)
        canvas.delete("status_text"), #remove processing text
        show_result(elapsed)
    root.after(0, update_gui)

if __name__ == "__main__":
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

    # notebook = ttk.Notebook(frame)
    # notebook.pack(fill = "both", expand = True)

    # wiki_tab = Frame(notebook, bg= "white")
    # reddit_tab = Frame(notebook, bg="white")

    # notebook.add(wiki_tab, text = "wikipedia")
    # notebook.add(reddit_tab, text = "reddit")

    #dropdown menu
    methods = ["Baseline", "MultiThreading", "Forking"] #different scraping methods
    opt = StringVar(root)
    opt.set(methods[0]) #default value

    promptLabel = Label(frame, text="Select a scraping method:", font=("Times New Roman", 14, "bold"))
    promptLabel.pack(pady=20)

    OptionMenu(frame, opt, *methods).pack(pady=10)

    websites = ["Wikipedia", "Reddit"]
    website_opt = StringVar(root)
    website_opt.set(websites[0]) #default (wiki)

    websiteLabel = Label(frame, text="Select a website to scrape: ", font = ("Times New Roman",14, "bold"))
    websiteLabel.pack(pady=20)
    OptionMenu(frame, website_opt, *websites).pack(pady = 10)

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
            # canvas.create_text(300, 40, text="baseline def/description....", font=("Arial", 10))
            
            # box
            canvas.create_rectangle(200, 80, 400, 120, fill="#a3989c", outline="#290f19", width=2)
            canvas.create_text(300, 100, text = "shared memory", font=("Arial", 12, "italic"))

            # single thread
            points = [300, 130, 290, 140, 310, 150, 290, 160, 300, 170] #curved line
            canvas.create_line(points, fill = "#572a3b", width=2, smooth=True)
            canvas.create_text(300, 210, text="Processing...", font=("Arial", 12), tags="status_text") 

            # for i, color in enumerate(["#a9a9a9", "#8b8b8b", "#696969","#484848", "#303030"]):
            #     x = 50 + i *100
            #     canvas.create_rectangle(x, 80, x+80, 120, fill=color, outline="")
            #     canvas.create_text(x+40, 150, text=f"Thread {i+1}", font=("Arial", 10))
        elif method == "MultiThreading":
            canvas.create_text(300, 20, text="multi-threading diagram", font = ("Arial", 16, "bold"))
            # canvas.create_text(300, 40, text="multithreading def/description....", font=("Arial", 10))
            
            canvas.create_rectangle(200, 80, 400, 120, fill="#a3989c", outline="#290f19", width=2)
            canvas.create_text(300, 100, text = "shared memory", font=("Arial", 12, "italic"))

            # multiple threads
            thread_colors = ["#31121e", "#4d2132", "#623748", "#905f71", "#bf99a8"]
            x_positions = [240, 270, 300, 330, 360]
            
            for i, x in enumerate(x_positions):
                points = [x, 130, x-10, 140, x+10, 150, x-10, 160, x, 170] #curved line for each thread
                canvas.create_line(points, fill = thread_colors[i % len(thread_colors)], width = 2, smooth = True)
            canvas.create_text(300, 210, text="Processing...", font=("Arial", 12), tags="status_text")

            # for i, color in enumerate(["#696969", "#696969", "#696969","#696969", "#696969"]):
            #     y = 60 + i *25
            #     canvas.create_rectangle(80, y, 520, y+20, fill=color, outline="")
            #     canvas.create_text(300, y+10, text=f"Thread {i+1}", font=("Arial", 10))
        elif method == "Forking":
            canvas.create_text(300, 20, text="forking diagram", font = ("Arial", 16, "bold"))
            #canvas.create_text(300, 40, text="forking def/description....", font=("Arial", 10))

            # forking diagram
            start_x = 115
            box_width = 100
            gap = 40
            process_colors = ["#4d2132", "#623748", "#905f71"]

            for i in range(3):
                x1 = start_x + i * (box_width + gap)
                x2 = x1 + box_width
                y1, y2 = 80, 120
                canvas.create_rectangle(x1, y1, x2, y2, fill=process_colors[i%len(process_colors)], outline = "#290f19", width=2)
                canvas.create_text((x1+x2)/2, 100, text = f"memory {i+1}", font=("Arial", 12, "italic"), fill="white")

                # curved lines
                points = [(x1+x2)/2, 130, (x1+x2)/2 - 10, 140, (x1+x2)/2 +10, 150, (x1+x2)/2 - 10, 160, (x1+x2)/2, 170]
                canvas.create_line(points, fill="#4d2132", width=2, smooth=True)
                canvas.create_text((x1+x2)/2, 180, text = f"Process {i+1}", font=("Arial", 12))
                canvas.create_text(300, 210, text="Processing...", font=("Arial", 12), tags="status_text")

    #display the result
    def show_result(time_value):
        canvas.create_text(300, 210, text=f"Total Time: {time_value} seconds", font=("Arial", 12), fill="#709958")

    # result box
    result_frame = Frame(frame, bg="white", bd=2, relief="sunken")
    result_frame.pack(fill="both", expand=True, padx=20, pady=(0,10))

    scrollbar = Scrollbar(result_frame)
    scrollbar.pack(side="right", fill="y")

    result_box = Text(result_frame, height = 10, wrap="word", yscrollcommand=scrollbar.set, bg="#d2cfd0", fg="black", font=("Arial", 12))
    result_box.pack(fill="both", expand=True)
    scrollbar.config(command=result_box.yview)

    #footer
    footerFrame = Frame(root, bg="#572a3b")
    footerFrame.pack(fill="x", side="bottom")
    footer = Label(footerFrame, 
                text="CS4310 - Fall 2025 | Parallel Processing Project", 
                bg = "#572a3b", fg="white", font=("Times New Roman", 14))
    footerNames = Label(footerFrame, text = "Arin Boyadjian, Jessica Pinto, Kaitlin Yen", bg="#572a3b", fg="white", font=("Times New Roman", 12))
    footer.pack(pady=5)
    footerNames.pack(pady=(0,5))

    root.mainloop()
