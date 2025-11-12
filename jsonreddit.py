import urllib.request
import json

# Example: top posts from r/webscraping
subreddit = "webscraping"
json_url = f"https://www.reddit.com/r/{subreddit}/top.json?limit=10&t=all"

# Reddit requires a User-Agent header, otherwise you may get blocked or empty results
headers = {'User-Agent': 'Mozilla/5.0 (compatible; Python WebScraper 1.0)'}

req = urllib.request.Request(json_url, headers=headers)

try:
    with urllib.request.urlopen(req) as url:
        data = json.loads(url.read())

    # Posts in data['data']['children']
    posts = data['data']['children']

    print(f"\nTop 10 posts from r/{subreddit}:\n")

    for i, post in enumerate(posts, start=1):
        post_data = post['data']
        title = post_data['title']
        author = post_data['author']
        upvotes = post_data['ups']
        comments = post_data['num_comments']
        link = "https://www.reddit.com" + post_data['permalink']
        text = post_data.get('selftext', '')  # Main post content

        # If text long shorten it
        short_text = (text[:1000] + "...") if len(text) > 200 else text

        # If no text must be link or media
        if text == "":
            short_text = "[No text content]"

        print(f"{i}. {title}")
        print(f"   Author: {author}")
        print(f"   Upvotes: {upvotes}")
        print(f"   Comments: {comments}")
        print(f"   URL: {link}\n")
        print(f"   Post Text: {short_text}\n")

except urllib.error.URLError as e:
    print(f"Error accessing URL: {e.reason}")
except json.JSONDecodeError as e:
    print(f"Error decoding JSON: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
