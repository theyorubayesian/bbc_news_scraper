import argparse
import csv
import itertools
import glob
import logging
import multiprocessing
import os
import time
from functools import partial
from typing import Dict, List, Optional, Tuple, Callable

import pandas as pd
import requests
import yaml
from bs4 import BeautifulSoup

from helpers import clean_string
from helpers import is_valid_url_factory

logging.root.setLevel(logging.INFO)

CONFIG = yaml.load(open("config.yml"), Loader=yaml.FullLoader)
ALL_CATEGORIES = CONFIG["CATEGORY_URLS"]


def get_parser() -> argparse.ArgumentParser:
    """
    parse command line arguments

    returns:
        parser - ArgumentParser object
    """
    parser = argparse.ArgumentParser(
        prog="BBC-Scraper",
        description="BBC News Website Scraper",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog="Written by: Akintunde 'theyorubayesian' Oladipo <akin.o.oladipo at gmail dot com>"
    )
    parser.add_argument(
        "--language",
        type=str,
        help="Language of BBC Website"
    )
    parser.add_argument(
        "--output_file_name", 
        type=str, 
        default="bbc_pidgin_corpus.csv", 
        help="Name of output file",
        )
    parser.add_argument(
        "--no_of_articles", 
        type=int, 
        default=-1,
        help="Number of articles to be scraped from the BBC pidgin website"
             "If -1, we scrape all articles we find",
        )
    parser.add_argument(
        "--categories", 
        type = str, 
        default= "all", 
        help= "Specify what news categories to scrape from." 
              "Multiple news categories should be separated by a comma. eg. 'africa,world,sport'",
        )
    parser.add_argument(
        "--time_delay", 
        type = bool, 
        default= True, 
        help= "Specify time delay after every url request",
        )
    
    parser.add_argument(
        "--spread",
        action="store_true",
        help="""Spread `no_of_articles` evenly across categories. If `most_popular` in categories, 
        all its articles are collected and the remainder is spread across other categories"""
    )
    
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Remove sub-topic TSV files created after combining them into final corpora"
    )
    return parser


def get_page_soup(url:str) -> BeautifulSoup:
    """
    Makes a request to a url and creates a beautiful soup oject from the response html

    input:
        :param url: input page url
    returns:
        - page_soup: beautiful soup oject from the response html
    """

    response = requests.get(url)
    page_html = response.text
    page_soup = BeautifulSoup(page_html, "html.parser")

    return page_soup


def get_page_count(soup: BeautifulSoup) -> int:
    count = 1
    ul: BeautifulSoup = soup.find_all("ul", attrs={"class": CONFIG["ARTICLE_COUNT_SPAN"]})
    
    if ul:
        count = int(ul[0].find_all("li")[-1].text)
    
    return count


def get_valid_urls(category_page: BeautifulSoup, is_valid_url: Callable) -> List[str]:
    """
    Gets all valid urls from a category page

    input:
        :param: url: category_page
    returns:
        - valid_urls: list of all valid article urls on a given category page
    """
    all_urls = category_page.findAll("a")
    valid_article_urls = []
    for url in all_urls:
        href: str = url.get("href")
        if is_valid_url(href):
            story_url = "https://www.bbc.com" + href if href.startswith("/") else href
            valid_article_urls.append(story_url)

    return list(set(valid_article_urls))


def get_urls(
    category_url:str, 
    category:str, 
    time_delay:bool,
    lang: str,
    articles_per_category: Optional[int] = None, 
    ) -> List[str]:
    """
    Obtains all the article urls from the category url it takes in

    input:
        :param categpry_url: category url
        :param category: category name
    returns:
        - category_urls: list of all valid article urls on all the category pages
    """
    page_soup = get_page_soup(category_url)
    category_urls = get_valid_urls(page_soup, is_valid_url_factory[lang])
    logging.info(f"{len(category_urls)} urls in page 1 gotten for {category}")

    if articles_per_category > 0 and len(category_urls) >= articles_per_category:
        return category_urls
    
    total_page_count = get_page_count(page_soup)
    logging.info(f"{total_page_count} pages found for {category}")
        
    for count in range(1, total_page_count):
        page_soup = get_page_soup(category_url + f"?page={count+1}")
        page_urls = get_valid_urls(page_soup, is_valid_url_factory[lang])
        logging.info(f"{len(page_urls)} urls in page {count+1} gotten for {category}")
        category_urls+=page_urls
        
        if articles_per_category > 0 and len(category_urls) >= articles_per_category:
            break
        
        if time_delay: 
            time.sleep(10)
    
    return category_urls


def get_article_data(article_url:str) -> Tuple[Optional[str], Optional[str], str]:
    """
    Obtains paragraphs texts and headlines input url article

    input:
        :param article_url: category_page
    returns:
        - headline: headline of url article 
        - story_text: text of url article
        - article_url: input article url
    """
    page_soup = get_page_soup(article_url)

    for cls_name in CONFIG["HEADLINE_SPAN_CLASS_A"]:
        headline = page_soup.find(
            "h1", attrs={"class": cls_name}
            )
        if headline:
            break

    if not headline:
        for cls_name in CONFIG["HEADLINE_SPAN_CLASS_B"]:
            headline = page_soup.find(
                "strong", attrs={"class": cls_name}
                )
            if headline:
                break
    
    if headline:
        headline = headline.text.strip()
    
    story_text = " "
    story_div = page_soup.find_all(
        "div", attrs={"class": CONFIG["STORY_DIV_CLASS"]}
        )
    if story_div:
        all_paragraphs = [div.findAll("p", recursive=False) for div in story_div]
        all_paragraphs = list(itertools.chain(*all_paragraphs))
        story_text = [p.text.strip().replace("\r", "").replace("\n", "\\n") for p in all_paragraphs]
        story_text = " ".join(story_text)
    story_text = story_text.strip() if not story_text == " " else None

    return (headline, story_text, article_url)


def get_topics(homepage: str, known_topic_urls: List[str], lang: str) -> Dict[str, str]:
    """
    Meant to be used with the homepage to recover all sub-topics available
    """
    page_soup = get_page_soup(homepage)
    article_urls = get_valid_urls(page_soup, is_valid_url_factory[lang])
    topics = {}

    for url in article_urls:
        url_soup = get_page_soup(url)
        
        for cls_name in CONFIG["TOPIC_LIST_CLASS"]:
            topic_elements = url_soup.find_all("li", attrs={"class": cls_name})
            if topic_elements:
                break
        
        for topic in topic_elements:
            topic_url = "https://www.bbc.com" + topic.find("a").get("href")
            if topic_url not in known_topic_urls:
                topic_name = topic.text
                topics[topic_name] = topic_url
    return topics


def write_articles(category, output_file_name, urls, no_of_articles, time_delay):
    path = output_file_name.split("/")
    output_file_name = os.path.join(path[0], f"{clean_string(category)}_{path[1]}")
    with open(output_file_name, "w", encoding = "utf-8") as csv_file:
        headers = ["headline", "text", "category", "url"]
        writer = csv.DictWriter(csv_file, delimiter="\t", fieldnames = headers, lineterminator='\n')
        writer.writeheader()
        story_num = 0

        logging.info(f"Writing articles for {category} category...")
        for url in urls:
            headline, paragraphs, url = get_article_data(url)
            if paragraphs:
                writer.writerow({
                    headers[0]:headline, 
                    headers[1]:paragraphs, 
                    headers[2]:category, 
                    headers[3]:url,
                    })
                story_num+=1
                logging.info(f"Successfully wrote story number {story_num}")

            if story_num == no_of_articles:
                logging.info(
                    f"Requested total number of articles {no_of_articles} reached"
                    )
                logging.info(
                    f"Scraping done. A total of {no_of_articles} articles were scraped!"
                    )
                return
            if time_delay: 
                time.sleep(10)
        logging.info(
        f"Scraping done. A total of {story_num} articles were scraped!"
        )


def scrape(url, category, time_delay, articles_per_category, output_file_name, lang):
    """
    Main function for scraping and writing articles to file
    
    input:
        :param output_file_name: file name where output is saved
        :param no_of_articles: number of user specified articles to scrape
        :param category_urls: all articles in a category
    """
    logging.info(f"Getting stories for {category}...")
    category_story_links = get_urls(url, category, time_delay, lang, articles_per_category)
    
    # category_urls[category] = category_story_links
    # json.dump(category_story_links, open(f"{category}_story_links.json", "w"), indent=4)
    logging.info(f"{len(category_story_links)} stories found for {category} category")

    # Note: Articles for each category is written to a separate file
    write_articles(
        category, 
        output_file_name, 
        category_story_links,
        articles_per_category,
        time_delay
    )


if __name__ == "__main__":

    logging.info("--------------------------------------")
    logging.info("Starting scraping...")
    logging.info("--------------------------------------")

    # initialize parser
    parser = get_parser()
    params, _ = parser.parse_known_args()
    
    # specify categories to scrape
    if params.categories != "all":
        categories = params.categories.upper().split(",")
        categories = {category: ALL_CATEGORIES[params.language][category] for category in categories}
    else:
        categories = ALL_CATEGORIES[params.language]
        other_categories = get_topics(CONFIG["HOMEPAGE"][params.language], list(categories.values()), params.language)
        categories.update(other_categories)

    articles_per_category = params.no_of_articles
    if params.no_of_articles > 0 and params.spread:
        if "MOST_POPULAR" in categories:
            # most_popular only has one page and 10 articles only
            # subtract this from no_of_articles to be collected before spreading
            articles_per_category = (params.no_of_articles-10) // (len(categories)-1)
        else:
            articles_per_category = round(params.no_of_articles / len(categories))
        
        articles_per_category = max(1, articles_per_category)
        logging.info(f"Will collect at least {articles_per_category} stories per category")
    
    pool = multiprocessing.Pool()
    processes = [
        pool.apply_async(
            scrape,
            args=(
                url,
                category,
                params.time_delay,
                articles_per_category,
                params.output_file_name,
                params.language
            )
        ) for category, url in categories.items()
    ]
    result = [p.get() for p in processes]

    path = params.output_file_name.split("/")
    output_file_pattern = os.path.join(path[0], f"*_{path[1]}")
    category_file_names = glob.glob(output_file_pattern)

    reader = partial(pd.read_csv, sep="\t", lineterminator="\n")
    all_dfs = map(reader, category_file_names)
    corpora = pd.concat(all_dfs).drop_duplicates(subset="url", keep="last")
    corpora.to_csv(params.output_file_name, sep="\t", index=False)

    if params.cleanup:
        for f in category_file_names:
            os.remove(f)

