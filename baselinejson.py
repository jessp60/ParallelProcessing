from multiprocessing import Process
import urllib.request
import json
import os
import csv

def child_fetch_top_posts(subreddit, limit=10):
    json_url = f"https://www.reddit.com/r/{subreddit}/top.json?limit={limit}&t=all"
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; Python WebScraper 1.0)'}
    req = urllib.request.Request(json_url, headers=headers)

    try:
        print(f"\nTop {limit} posts from r/{subreddit} (PID {os.getpid()}):\n")

        # Read json data from Reddit into data
        with urllib.request.urlopen(req) as url:
            data = json.loads(url.read())
        # Posts in data['data']['children'] into posts
        posts = data['data']['children']

        # Create a CSV file for this subreddit
        filename = f"baseline_{subreddit}_top_posts.csv"
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
                short_text = (text[:1000] + "...") if len(text) > 200 else text

                # If no text must be link or media
                if text == "":
                    short_text = "[No text content]"
            
                writer.writerow([i, title, author, upvotes, comments, link, short_text])
                print(f"Process {os.getpid()} fetched post {i} from r/{subreddit}: {title}")
        
    except urllib.error.URLError as e:
        print(f"Error accessing URL: {e.reason}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")



if __name__ == "__main__":
    subreddits = ["webscraping", "learnpython", "datascience"]
    processes = []

    # Spawn a process for each subreddit
    for subreddit in subreddits:
        p = Process(target=child_fetch_top_posts, args=(subreddit, 10))
        # No parallel processing, blocks rest of the code temporarily
        p.run()
        print(f"Spawned process {p.pid} for subreddit: {subreddit}")
        processes.append(p)
    
    # Display process completion
    for p in processes:
        print(f"Process {p.pid} completed.")
    
    print("\n All data retrieved. Program exiting cleanly.")