# environment ~/Documents/GitHub/ParallelProcessing/.venv/bin/python
import tkinter as tk
from tkinter import messagebox
import csv
import threadingjson, forkingjson
from multiprocessing import Process, Queue
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import os
import urllib.request
import json
import numpy as np


# Reddit sequential runner
def run_reddit_sequential(subreddits=None, limit=10):
    results = []

    startTime = time.perf_counter()
    # Process each subreddit one after another
    for subreddit in subreddits:
        threadingjson.child_fetch_top_posts(subreddit, results, limit)
        # results.append(f"Completed fetching posts for subreddit: {subreddit}")
    
    endTime = time.perf_counter()
    elapsed = round(endTime-startTime, 3)
    results.append(f"\nTotal Sequential Processing Time: {elapsed} seconds")

    return elapsed


if __name__ == "__main__":
    # Define subreddits to scrape
    subreddits = ["webscraping", "learnpython", "datascience", "MachineLearning", "Python", "programming", "computerscience", "technology", "coding", "bigdata"]

    # Initialize time accumulators
    baseline_times = []
    multithreading_times = []
    forking_times = []

    # Get test parameters
    size = 30
    print("Enter number of subreddits to scrape per test (max 10): ")
    num_subs = int(input().strip())
    print("Enter number of posts to scrape per test (e.g., 10, 20, 30): ")
    limit = int(input().strip())

    # Print test parameters
    print(f"Number of Tests: {size}")
    print(f"Number of Subreddits: {num_subs}")
    print(f"Number of Pages per Test: {limit}")
    print("\nStarting tests...")
    print("-" * 70)

    # Run tests
    for i in range(size):
        baseline_times.append(run_reddit_sequential(subreddits[:num_subs], limit))
        multithreading_times.append(threadingjson.run_reddit_multithreading(subreddits[:num_subs], limit))
        forking_times.append(forkingjson.run_reddit_forking(subreddits[:num_subs], limit))
    
    avr_baseline = np.round(np.mean(baseline_times), 3)
    avr_multithreading = np.round(np.mean(multithreading_times), 3)
    avr_forking = np.round(np.mean(forking_times), 3)

    std_baseline = np.round(np.std(baseline_times), 3)
    std_multithreading = np.round(np.std(multithreading_times), 3)
    std_forking = np.round(np.std(forking_times), 3)

    print("-" * 70)
    print("\nTest Results:")
    print(f"\nAverage Baseline Time: {avr_baseline} seconds")
    print(f"\nAverage Threading Time: {avr_multithreading} seconds")
    print(f"\nAverage Forking Time: {avr_forking} seconds")

    # Add to csv file
    if not os.path.exists("results_reddit.csv"):
        with open("results_reddit.csv", mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Method", "Average Time (seconds)", "Number of Subreddits", "Posts per Subreddit", "Standard Deviation (seconds)"])
    with open("results_reddit.csv", mode="a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Baseline", avr_baseline, num_subs, limit, std_baseline])
        writer.writerow(["MultiThreading", avr_multithreading, num_subs, limit, std_multithreading])
        writer.writerow(["Forking", avr_forking, num_subs, limit, std_forking])