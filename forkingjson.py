#reddit forking

from multiprocessing import Manager, Process
import urllib.request
import json
import os
import csv
import time

def child_fetch_top_posts(subreddit, results, limit=13):
    json_url = f"https://www.reddit.com/r/{subreddit}/top.json?limit={limit}&t=all"
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; Python WebScraper 1.0)'}
    req = urllib.request.Request(json_url, headers=headers)

    try:
        header = f"\nTop {limit} posts from r/{subreddit} (PID {os.getpid()}):\n"
        # print (header)
        results.append(header)

        # Read json data from Reddit into data
        with urllib.request.urlopen(req) as url:
            data = json.loads(url.read())
        # Posts in data['data']['children'] into posts
        posts = data['data']['children']

        # Create a CSV file for this subreddit
        filename = f"forking_{subreddit}_top_posts.csv"
        with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Index", "Title", "Author", "Upvotes", "Comments", "URL", "Post Text"])
        
            # Output post details
            for i, post in enumerate(posts, start=1):
                post_data = post['data']
                title = post_data['title']
                author = post_data['author']
                upvotes = post_data['ups']
                comments = post_data['num_comments']
                link = "https://www.reddit.com" + post_data['permalink']
                text = post_data.get('selftext', '')

                # If text long shorten it
                short_text = (text[:200] + "...") if len(text) > 200 else text

                # If no text must be link or media
                if text == "":
                    short_text = "[No text content]"
            
                writer.writerow([i, title, author, upvotes, comments, link, short_text])
                formatted_posts = (f"Post {i}:\n" f"    Title: {title}\n"f"    Author: {author}\n"f"    Upvotes: {upvotes}\n"f"    Comments: {comments}\n" f"    URL: {link}\n" f"    Text: {short_text}\n")
                results.append(formatted_posts)
                results.append("")
            #     results.append(f"Process {os.getpid()} fetched post {i} from r/{subreddit}: {title}")

            # results.append("") #empty line after each subreddit
        
    except urllib.error.URLError as e:
        error1 = f"Error accessing URL: {e.reason}"
        print(error1)
        results.append(error1)

    except json.JSONDecodeError as e:
        error2 = f"Error decoding JSON: {e}"
        print(error2)
        results.append(error2)

    except Exception as e:
        error3 = f"Unexpected error: {e}"
        print(error3)
        results.append(error3)



def run_reddit_forking(subreddits, limit):
    manager = Manager() # allows parallel execution of the code
    results = manager.list() 
    processes = []
    subreddits = ["webscraping"]

    startTime = time.perf_counter()
    # Spawn a process for each subreddit
    for subreddit in subreddits:
        p = Process(target=child_fetch_top_posts, args=(subreddit, results, limit))
        # Begins executing processes in parallel
        p.start()
        results.append(f"Spawned process {p.pid} for subreddit: {subreddit}")
        processes.append(p)
    
    # Wait for all processes to complete
    for p in processes:
        p.join()
        # print(f"Process {p.pid} completed.")
    
    endTime = time.perf_counter()
    elapsed = round(endTime-startTime, 3)
    results.append(f"\nTotal Forking Processing Time: {elapsed} seconds")

    # return elapsed, list(results)
    return elapsed