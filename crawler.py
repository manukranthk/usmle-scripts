'''
A web crawler for extracting email addresses from web pages.

Takes a string of URLs and requests each page, checks to see if we've
found any emails and prints each email it finds.
'''

#python crawler.py --urls https://med.uth.edu/pediatrics/adolescent-medicine/,https://med.uth.edu/pediatrics/cardiology/,https://med.uth.edu/pediatrics/community-general-pediatrics/,https://med.uth.edu/pediatrics/critical-care-medicine/,https://med.uth.edu/pediatrics/endocrinology/,https://med.uth.edu/pediatrics/gastroenterology/,https://med.uth.edu/pediatrics/hematology/,https://med.uth.edu/pediatrics/infectious-diseases/,https://med.uth.edu/pediatrics/medical-genetics/,https://med.uth.edu/pediatrics/neonatology/,https://med.uth.edu/pediatrics/nephrology-hypertension/,https://med.uth.edu/pediatrics/neurology/,https://med.uth.edu/pediatrics/pediatric-hospital-medicine/,https://med.uth.edu/pediatrics/pediatric-research-center/

#python crawler.py --urls https://dellmed.utexas.edu/search?searchCriteria=eyJnIjoiZGlyZWN0b3J5IiwiZiI6W3siaWQiOiI5IiwidmFsdWUiOlsiNDg0OSJdfV19

import argparse
import html
import re
import sys
import urllib.request as urllib2
from bs4 import BeautifulSoup
import requests
import requests.exceptions
from urllib.parse import urlsplit
from collections import deque


class Crawler(object):

    def __init__(self, urls):
        '''
        @urls: a string containing the (comma separated) URLs to crawl.
        '''
        self.urls = urls.split(',')

    def crawl(self):
        '''
        Iterate the list of URLs and request each page, then parse it and
        print the emails we find.
        '''

        # a queue of urls to be crawled
        new_urls = deque(self.urls)
        processed_urls = set()
        emails = set()

        while len(new_urls):
            url = new_urls.popleft()
            processed_urls.add(url)

            parts = urlsplit(url)
            base_url = "{0.scheme}://{0.netloc}".format(parts)
            path = url[:url.rfind('/')+1] if '/' in parts.path else url
            # get url's content
            print("Processing %s" % url)
            regex = r'mailto:.*.edu">'
            if url.find('utexas.edu') >= 0:
                regex = r'mailto:.*.edu">'
            elif url.find('uth.edu') >= 0:
                regex = r'mailto:.*">.*M.D.'

            try:
                response = requests.get(url)
            except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL):
                continue # skip the page

            try:
                new_emails = set([html.unescape(re.search(regex, response.text, re.I).group(0))])
                emails.update(new_emails)
            except:
                pass
            print(emails)
            # print(new_urls)

            # create a beutiful soup for the html document
            soup = BeautifulSoup(response.text, "lxml")

            # find and process all the anchors in the document
            for anchor in soup.find_all("a"):
                # extract link url from the anchor
                link = anchor.attrs["href"] if "href" in anchor.attrs else ''
                # resolve relative links
                if link.startswith('/'):
                    link = base_url + link
                elif not link.startswith('http'):
                    link = path + link
                # add the new url to the queue if it was not enqueued nor processed yet
                if not link in new_urls and not link in processed_urls:
                    if link.find('pediatrics') >= 0:
                        new_urls.append(link)
        print(emails)

    @staticmethod
    def request(url):
        '''
        Request @url and return the page contents.
        '''
        response = urllib2.urlopen(url)
        return response.read()

    @staticmethod
    def process(data):
        '''
        Process @data and yield the emails we find in it.
        '''
        for email in [re.search(r'mailto:.*">.*M.D.', data).group(0)]:
            yield email


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        '--urls', dest='urls', required=True,
        help='A comma separated string of emails.')
    parsed_args = argparser.parse_args()
    crawler = Crawler(parsed_args.urls)
    crawler.crawl()


if __name__ == '__main__':
  sys.exit(main())
