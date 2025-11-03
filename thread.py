import threading 
from requests_html import HTML, HTMLSession 

class thread(threading.Thread): 
    def __init__(self, thread_name, thread_ID):
        threading.Thread.__init__(self)
        self.thread_name = thread_name 
        self.thread_ID = thread_ID 

    def run(self, pageName): 
        session = HTMLSession()
        print(str(self.thread_name) + " " + str(self.thread_ID) + " is running.") 
        threadURL = f"https://en.wikipedia.org/wiki/Wikipedia:Contents/{pageName}"
        thread = session.get(threadURL)
        threadOverview = thread.html.find("h2")
        if threadOverview: 
            print("Items on page:")
            for overview in threadOverview: 
                print("-", overview.text) 