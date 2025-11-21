# environment ~/Documents/GitHub/ParallelProcessing/.venv/bin/python

import csv
import baselinejson, threadingjson, forkingjson
from requests_html import HTML, HTMLSession 
from multiprocessing import Process, Queue
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import time, io, sys

def get_session():
    return HTMLSession()

#wiki scraper function
from requests_html import HTMLSession
import re

session = HTMLSession()

def is_noise_paragraph(text):
    """Return True if this paragraph looks like noise (coords, empty, tiny, etc)."""
    if not text:
        return True
    txt = text.strip()
    # very short
    if len(txt) < 40:
        return True
    # coordinates / pronunciation / language templates often contain unusual punctuation
    # skip pure bracketed coordinates like "(...)" or strings that start with '['
    if re.match(r'^\[.*\]$', txt) or txt.startswith('Coordinates') or txt.startswith('•'):
        return True
    # skip if paragraph is basically only citation markers or punctuation
    if re.match(r'^[\[\]\d\W]+$', txt):
        return True
    return False

def get_wiki_intro(title, min_chars=120, max_accumulate=1200):
    """
    Return a robust introduction for a Wikipedia article title (string with underscores or spaces).
    It collects direct child <p> elements in div.mw-parser-output, skipping noise, and may
    join several consecutive paragraphs until min_chars or max_accumulate is reached.
    """
    url = f"https://en.wikipedia.org/wiki/{title}"
    r = session.get(url)
    # select direct child <p> inside the article body
    paras = r.html.find('div.mw-parser-output > p')
    intro_parts = []
    accumulated = 0

    for p in paras:
        text = p.text or ""
        # some <p> may only contain a reference span; treat as empty
        text = text.strip()
        if is_noise_paragraph(text):
            # skip and continue scanning
            continue

        # looks like a real paragraph — add it
        intro_parts.append(text)
        accumulated += len(text)

        # stop if we've collected a decent-sized intro
        if accumulated >= min_chars or accumulated >= max_accumulate:
            break

    # fallback: if nothing found in direct <p> children, attempt to find first <p> anywhere
    if not intro_parts:
        p_any = r.html.find('p', first=True)
        if p_any and p_any.text and not is_noise_paragraph(p_any.text.strip()):
            intro_parts = [p_any.text.strip()]

    if not intro_parts:
        return "No description found."

    # join paragraphs with double newline for readability
    return "\n\n".join(intro_parts)


# Example usage inside your existing wiki_scrape_page:
def wiki_scrape_page(title, queue=None):
    url = f"https://en.wikipedia.org/wiki/{title}"
    try:
        intro = get_wiki_intro(title)
        filename = f"wiki_{title}.csv"
        with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Index", "Title", "Post Text"])
            writer.writerow([i, title, intro])
        
    except Exception as e:
        intro = f"Error scraping {title}: {e}"

    # print(f"{title}: {intro[:300]}...\n")

    if queue:
        queue.put((title, intro))

    return intro

def wiki_get_titles(limit):
    url = 'https://en.wikipedia.org/wiki/Wikipedia:Contents/Technology_and_applied_sciences'
    session = get_session()
    r = session.get(url)

    links = r.html.find('a[href^="/wiki/"]')

    titles = set()

    for link in links:
        href = link.attrs.get("href", "")

        if not href.startswith("/wiki/"):
            continue
        if ":" in href:  # filters File:, Category:, Help:, etc.
            continue
        if href.startswith("/wiki/Wikipedia:"):
            continue

        titles.add(href.replace("/wiki/", ""))

        if len(titles) >= limit:
            break

    return list(titles)


# baseline scraper function
# define limit of pages to scrape
def wiki_baseline_scraper(limit):
    titles = wiki_get_titles(limit=limit)

    startTime = time.perf_counter()
    for title in list(titles):
        wiki_scrape_page(title)
    endTime = time.perf_counter()
    elapsed = round(endTime - startTime, 3)
    print(f"\nTotal Baseline Processing Time: {elapsed} seconds")
    return elapsed

# multithreading scraper function
# define limit of pages to scrape
def wiki_multithreading_scraper(limit):
    titles = wiki_get_titles(limit=limit)

    startTime = time.perf_counter()
    threads = []
    for title in titles:
        t = threading.Thread(target=wiki_scrape_page, args=(title,))
        t.start()
        threads.append(t)

    for index, t in enumerate(threads):
        t.join()
        # print(f"Thread {index} completed.")

    endTime = time.perf_counter()
    elapsed = round(endTime - startTime, 3)
    print(f"\nTotal MultiThreading Processing Time: {elapsed} seconds")
    return elapsed

# forking scraper function
# define limit of pages to scrape
def wiki_forking_scraper(limit):
    titles = wiki_get_titles(limit)

    queue = Queue()
    processes = []

    startTime = time.perf_counter()

    for title in titles:
        p = Process(target=wiki_scrape_page, args=(title, queue))
        p.start()
        processes.append(p)

    for index, p in enumerate(processes):
        p.join()
        # print(f"Process {index} completed.")

    results = []
    while not queue.empty():
        results.append(queue.get())
    
    queue.close()
    queue.join_thread()

    elapsed = round(time.perf_counter() - startTime, 3)

    print(f"\nTotal Forking Processing Time: {elapsed} seconds")
    return elapsed


if __name__ == "__main__":
    # baseline_times = 0
    multithreading_times = 0
    forking_times = 0

    size = 30
    limit = 5

    for i in range(size):
        # baseline_times += wiki_baseline_scraper(limit)
        # multithreading_times += wiki_multithreading_scraper(limit)
        forking_times += wiki_forking_scraper(limit)
    # print(f"\nAverage Baseline Time: {round(baseline_times/size,3)} seconds")
    # print(f"\nAverage Threading Time: {round(multithreading_times/size,3)} seconds")
    print(f"\nAverage Forking Time: {round(forking_times/size,3)} seconds")