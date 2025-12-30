#!/bin/python3

'''
Welcome to ScrapeReddit (scReddit) V1.0
Command line tool for downloading Gifs from reddit
Tries to prevent duplicate downloads but no guarantee, If something was uploaded under multiple names its hard to tell
    Would like to add file hash checking but even that wont be 100%. Gifs are often changed in little ways before upload and it shifts the hash.

This script is still buggy but functional. If you know python you should be fine debugging any issues, they should be small.
This tool is provided as is with no guarantee.

Written and Tested on Ubuntu 24.04.3 LTS using Chrome Version 143.0.7499.169

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

# Im really not sure how this looks to reddit servers, so keep DL to slow pace

import argparse
import os
import re
import subprocess
from time import sleep
from redgifs import HTTPException
from selenium import webdriver
from selenium.webdriver.common.by import By
import redgifs

USER_PAUSE_TIME = 5
SCROLL_PAUSE_TIME = 1.0 #Pause between scrolling
DL_PAUSE_TIME = 1.0 #Wait time between downloads


# FUTURE FEATURES
# TODO Allow downloading from user pages as well as subs
# TODO Hash files and check hashes before DL
# TODO Allow downloading of text posts


class Manifest:
    def __init__(self):
        self.gif_list = set()
        self.number_new_gifs = 0

    def __add__(self, other):
        self.gif_list.add(other)
        if not other.local_file_found:
            self.number_new_gifs += 1

    def __contains__(self, item):
        for gif in self.gif_list:
            if gif.name == item:
                return True
        return False

    def get_total_gifs(self):
        return len(self.gif_list)

    def get_new_gifs(self):
        return self.number_new_gifs


class Gif:
    # init (unique filename string, filetype,source site, source url, is crosspost, local file found)
    # init (str, str, str, bool, bool)
    def __init__(self, name, format, source ,url, xpost, local_file_found):
        self.name = name
        self.format = format
        self.source = source
        self.url = url
        self.is_crosspost = xpost
        self.local_file_found = local_file_found
        # Backup is Null if none avaliable

    def display(self):
        cross = "No"
        if self.is_crosspost:
            cross = "Yes"
        print("\n-- Gif File Info --")
        print(f"Name: {self.name}\n"
              f"Source Site: {self.source}\n"
              f"FileType: {self.format}\n"
              f"URL: {self.url}\n"
              f"Crosspost: {cross}\n"
              f"Already Downloaded: {self.local_file_found}"
              )


    def new_gif_from_web(raw_url):
        cross = False
        regex = re.compile("https?://.*/")
        site = regex.match(raw_url).group()
        clean_url = raw_url.split("#")[0].split("?")[0].strip()
        base_info = clean_url.lower().split("/")[-1].split(".")

        clean_name = base_info[0].strip()
        gif_format = base_info[-1].strip()

        if DEBUG:
            print("DEBUG: Creating new Gif object for URL: " + str(raw_url))
            print(f"  -- GIF INFO --\n"
                  f"  Src URL: {raw_url}"
                  f"  Clean Name: {clean_name}"
                  f"  File Format: {gif_format}")
            #name,      format,  source site  ,url,  xpost, local_file_found
        return Gif(clean_name, gif_format, site,    clean_url,  cross,   False)

    def new_gif_from_file(filename):
        if DEBUG:
            print("Creating new Gif object from file: " + str(filename))
        split_file = filename.split()
        gif_format = split_file[-1].split(".")[-1]
        src = "placeholder"
        clean_url = "placeholder"
        cross = False
        return Gif(filename, gif_format, src, clean_url, cross, True)


    def new_gif_from_giphy(raw_url):
        # CASE MATTERS
        site = "https://media.giphy.com"
        clean_url = raw_url.split("#")[0].split("?")[0].strip()
        base_info = clean_url.split("/")
        clean_name = base_info[-2].strip()
        base_info = base_info[-1].split(".")
        gif_format = base_info[-1].strip()
        cross = False
        clean_url = site + "/media/" + clean_name + "/giphy.gif"
        return Gif(clean_name, gif_format, site, clean_url, cross, False)

    def new_dash_gif(dash_url):
        if dash_url == "":
            return None
        elif dash_url is None:
            print("Error: Could not find Dash Video URL")
            quit()
        site = "reddit"
        clean_name = dash_url.split("/")[2]
        if "gif" in dash_url:
            gif_format = "gif"
        elif "mp4" in dash_url:
            gif_format = "mp4"
        cross = False
        clean_url = dash_url
        return Gif(clean_name, gif_format, site, clean_url, cross, False)


def find_link_with_sound(url):
    sub_driver = webdriver.Chrome()
    sub_driver.get("https://reddit.com")
    sub_driver.get(url)
    final_video = ""
    player_elements = driver.find_elements(By.XPATH, "//shreddit-player")
    for element in player_elements:
        if element is not None:
            media_json = element.get_attribute("packaged-media-json")
            all_videos = []
            if media_json is not None:
                highest_quality = 0
                url_pattern = re.compile("https?://packaged-media.redd.it/[a-zA-Z0-9=/\-_\.?&]*")
                for item in re.findall(url_pattern, media_json):
                    if item is not None:
                        all_videos.append(str(item))
                        quality_pattern = re.compile("[0-9]+p")
                        quality_result = re.search(quality_pattern, item)
                        if quality_result is not None:
                            quality = int(quality_result.group().strip("p"))
                            if quality > highest_quality:
                                highest_quality = quality
                if len(all_videos) == 0:
                    print("Video not found")
                    continue
                for item in all_videos:
                    if str(highest_quality) in item:
                        final_video = item

    return final_video

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Reddit Downloader",
        description="A small tool to download gifs and images from reddit",
        usage='scReddit.py [options] -s <sub_to_scrape>'
    )

    parser.add_argument("-d", "--debug", action="store_true", default=False, help="Prints debug messages to console")
    parser.add_argument("-p", "--path", default="downloads", type=str, help="Location of file storage")
    parser.add_argument("-s", "--sub", type=str, help="Target sub to scrape, sub name only, not the web addr")
    parser.add_argument("-r", "--run", action="store_true", default=False, help="flag determines if we download files")
    parser.add_argument("-x", "--xpost", action="store_true", default=False, help="Tracks down and downloads cross posts")
    parser.add_argument("-l", "--list", action="store_true", default=False, help="Runs tool but only outputs found subreddits")
    parser.add_argument("-t", "--top", action="store_true", default=False, help="sorts by top, downloading the top gifs from the sub")
    parser.add_argument("-b", "--bulk", default=None, help="Allows bulk download reading subs from a file")
    parser.add_argument("-c", "--count", type=int, default=10, help="Number of pages to scroll before downloading")

    # Parse our args and transfer them to variables
    parsed_args = parser.parse_args().__dict__
    for key in parsed_args.keys():
        value = parsed_args.get(key)
        match key:
            case "debug":
                DEBUG = value
            case "sub":
                if value is None:
                    exit("Error: A subreddit path must be provided")
                else:
                    SUB = value
                    SUB_URL = "https://reddit.com/r/" + value
            case "path":
                DL_FOLDER = value
            case "run":
                DRY_RUN = (value == False)
            case "xpost":
                XPOST = value
            case "list":
                LIST_SUBS = value
            case "top":
                SORT_TOP = value
            case "bulk":
                BULK = True
                BULK_FILE = value
            case "count":
                MAX_PAGE_SCROLL = value



    ##########################################################################################
    cross_posts = set()
    # TODO add logic for bulk downloading
    if BULK:
        pass
    print("Starting Operations...")
    if DRY_RUN:
        print("Starting Dry Run\n     no files will be downloaded")
    if DEBUG:
        print("DEBUG: Running with Debug active")
    print("DEBUG: " + str(parsed_args))
    work_dir = os.getcwd()

    #Set our downloads folder path, using full path to be safe
    DL_PATH = work_dir + "/" + DL_FOLDER
    if not DL_FOLDER in os.listdir(work_dir):
        subprocess.run(["mkdir", DL_FOLDER])

    file_count = 0
    download_count = 0

    # Update manifest with all files found in the users dl directory
    manifest = Manifest()
    for filename in os.listdir(DL_PATH):
        if (".mp4" in filename) or (".gif" in filename):
            new_gif = Gif.new_gif_from_file(filename)
            if new_gif not in manifest:
                manifest.__add__(new_gif)
    #Open Chrome and pause for user to enter creds
    driver = webdriver.Chrome()
    driver.get('https://reddit.com')
    sleep(USER_PAUSE_TIME)
    try:
        if SORT_TOP:
            driver.get(SUB_URL + "/top/?t=all")
        else:
            driver.get(SUB_URL)
    except:
        print("ERROR: subreddit could not be found")
        quit()
    last_height = driver.execute_script("return document.body.scrollHeight")
    print("Starting Scraping...")
    page = 0
    new_urls = set()
    cross_posts = set()
    video_lst = []
    backup_videos = []
    while page <= MAX_PAGE_SCROLL:
        player_elements = driver.find_elements(By.XPATH, "//shreddit-player")
        for element in player_elements:
            if element is not None:
                final_video = ""
                test = element.get_attribute("packaged-media-json")
                all_videos = []
                if test is not None:
                    highest_quality = 0
                    url_pattern = re.compile("https?://packaged-media.redd.it/[a-zA-Z0-9=/\-_\.?&]*")
                    for item in re.findall(url_pattern, test):
                        if item is not None:
                            all_videos.append(str(item))
                            quality_pattern = re.compile("[0-9]+p")
                            quality_result = re.search(quality_pattern, item)
                            if quality_result is not None:
                                quality = int(quality_result.group().strip("p"))
                                if quality > highest_quality:
                                    highest_quality = quality
                    if len(all_videos) == 0:
                        print("Video not found")
                        continue
                    for item in all_videos:
                        if str(highest_quality) in item:
                            final_video = item
                dash_gif = Gif.new_dash_gif(final_video)
                if dash_gif is not None:
                    manifest.__add__(dash_gif)
        # web_elements = driver.find_elements(By.XPATH, "//shreddit-post")
        # for element in web_elements:
        #     raw_url = (element.get_attribute("content-href"))
        #     if "/r/" in raw_url:
        #         cross_posts.add(raw_url)
        #         continue
        #     # print("DEBUG: Raw urls: " + str(raw_url))
        #     elif "giphy" in raw_url:
        #         working_gif = Gif.new_gif_from_giphy(raw_url)
        #     else:
        #         working_gif = Gif.new_gif_from_web(raw_url)
        #     if working_gif not in manifest:
        #         if DEBUG:
        #             print("DEBUG: Found New URL: " + working_gif.url)
        #         manifest.__add__(working_gif)
        #         file_count += 1
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(SCROLL_PAUSE_TIME)
        page += 1

    # Create a backup list from posts and check that we didnt miss any gifs


# Cleaning up cross posts by tracking down the real page
    if XPOST:
        print("Tracking down cross posts...")
        if DEBUG:
            print("Current xpost list: " + str(cross_posts))
        if len(cross_posts) > 0:
            for post in cross_posts:
                if "/r/" in post:
                    try:
                        driver.get("https://reddit.com" + post)
                    except:
                        print("ERROR: X-Post sub could not be found: " + str(post))
                        continue
                    element = driver.find_element(By.XPATH, "//shreddit-post")
                    src = (element.get_attribute("content-href"))

                    working_gif = Gif.new_gif_from_web(src)
                    if working_gif not in manifest:

                        manifest.__add__(working_gif)
                        file_count += 1

    api = redgifs.API()
    api.login()
    if DRY_RUN:
        print("Starting Dry Run...")
        for gif in manifest.gif_list:
            if not gif.local_file_found:
                url = gif.url
                if "redgifs" in url:
                    print("DRY: redgifs -q hd " + url)
                else:
                    subprocess.run(["echo", "DRY: ", "wget " + url])
    else:
        print(f"found {file_count} new Gifs")
        print("Are you sure you want to download these files?")
        confirm = input("Please Confirm(Y): ")
        if confirm.upper() == "Y":
            os.chdir(DL_FOLDER)
            for gif in manifest.gif_list:
                if not gif.local_file_found:
                    url = gif.url
                    if "media.redd.it" in url or "giphy" in url:
                        subprocess.run(["wget", "--progress=bar:force", "--no-verbose", url])
                        sleep(DL_PAUSE_TIME)
                    if "redgifs" in url:
                        print("downloading: " + url)
                        try:
                            hd_url = api.get_gif(gif.name).urls.hd
                            api.download(hd_url, gif.name + ".mp4")
                            sleep(DL_PAUSE_TIME)
                        except HTTPException:
                            print("  ERROR: Gif Deleted")

                    # TODO add support for imgur
                    if "imgur" in url:
                        pass
                    # TODO add support for gifcen
                    if "gifcen" in url:
                        pass
                    # TODO add support for tenor
                    if "tenor" in url:
                        pass
                    # TODO add support for v.reddit
                    if "v.redd.it" in url:
                        pass
                    gif.local_file_found = True
                    download_count += 1
        else:
            print("Exiting...")



    # Cleanup
    # Make sure to close our selenium driver
    driver.quit()
    api.close()
    # Update the manifest file before closing
    subs_list = set()
    for post in cross_posts:
        subs_list.add(post.split("/")[2])
    if len(subs_list) == 0:
        subs_list = "None"
    print("\n--REPORT--")
    print("New Reddit Gifs Found: " + str(file_count))
    print("Cross Posts found: " + str(len(cross_posts)))
    print("Files Downloaded: " + str(download_count))
    print("Subreddits Found : " + str(subs_list))