import json
import logging
import os
import threading
import urllib2

from urllib2 import urlopen
from utils import *

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s', )


def parse_kr(whois_response):
    """

    :param whois_response: the resporse from the .kr whois server
    :return: whois_standard_dict with the data from the whois response
    """
    pass


whois_servers = {".kr": "http://whois.marcaria.com/domain-whois/asia/South-Korea-domain-KR?q=XXXXX",
                 "default": "https://www.whois.com/whois/XXXXX"}
tld_parse_functions = {".kr": parse_whois_response_kr,
                       "default": parse_whois_response_default}
whois_standard_dict = ["Domain Name", "Registrant Name", "Registrant City", "Registrant Country", "Name Server"]


def do_parse_writing(output_file_name, url_to_whois):
    with open(output_file_name, 'a') as outf:
        json.dump(url_to_whois, outf)
        outf.write('\n')


def do_parse2_writing(output_file_name, url_to_whois):
    with open(output_file_name, 'a') as outf:
        json.dump(url_to_whois, outf)
        outf.write(",")
        outf.write('\n')


def get_url_for_whois_request(whois_server_ending,url_origin):
    """
    Get url suitable for sending to get whois data for the original url.
    :param whois_server_ending: TLD of the original url, i.e ".com"
    :param url_origin: complete original url i.e "google.com"
    :return: new url of the specific TLD whois server with the original url in it ready for request
    """
    if whois_server_ending in whois_servers:
        whois_current_server = whois_servers[whois_server_ending]
        return whois_current_server.replace("XXXXX", url_origin)
    else:
        return whois_servers["default"].replace("XXXXX", url_origin)


class ThreadPool(object):
    def __init__(self):
        super(ThreadPool, self).__init__()
        self.active = []
        # lock to write to self.active list
        self.lock = threading.Lock()
        # lock to write to output file
        self.lock2 = threading.Lock()

    def makeActive(self, name):
        with self.lock:
            self.active.append(name)
            logging.debug('Running: %s', self.active)

    def makeInactive(self, name):
        with self.lock:
            self.active.remove(name)
            logging.debug('Running: %s', self.active)

    """
        Create Json object like this:
            {"string":"string1","int":1,"array":[1,2,3],"dict": {"key": "value1"}}
            {"string":"string2","int":2,"array":[2,4,6],"dict": {"key": "value2"}}
            {"string":"string3","int":3,"array":[3,6,9],"dict": {"key": "value3", "extra_key": "extra_value3"}}
    
    """

    def do_parse(self, line, output_file_name, u_a):
        url_origin = line.strip()
        if (url_origin.endswith(".")):
            url_origin = url_origin[:-1]
        whois_server_ending = get_tld(url_origin)
        r = ""
        text = ""
        print "WHOIS server ending is " + whois_server_ending
        url_for_whois_requests = get_url_for_whois_request(whois_server_ending,url_origin)

        # send the request for the whois data
        # r = requests.get(url_for_whois_requests, headers={"USER-AGENT": u_a})
        user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36'
        headers = {'User-Agent': user_agent}
        req = urllib2.Request(url_for_whois_requests, None, headers)
        r = urllib2.urlopen(req)
        # r = urllib2.urlopen(url_for_whois_requests)

        # get the HTML text from the response
        # text = r.text  # .decode('utf-8')
        text = r.read()


        if whois_server_ending in tld_parse_functions.keys():
            tld_parse_functions[whois_server_ending](text,url_origin, logging, self, do_parse_writing, output_file_name)
        else:
            tld_parse_functions["default"](text,url_origin, logging, self, do_parse_writing, output_file_name)

    def do_parse2(self, line, output, u_a):
        url_to_whois = {}
        url = line.strip()
        # send the request for the whois data
        request = requests.get(url, headers={"USER-AGENT": u_a})

        # get the HTML text from the response
        text = request.text  # .decode('utf-8')

        # The raw HTML for debug purposes
        raw_start = "<div class=\"whois_main_column\">"
        raw_end = "<div class=\"whois_rhs_column\">"
        rawHtml = text[text.index(raw_start) + len(raw_start): text.index(raw_end)]
        # print rawHtml

        # Start the scrapper
        start = "<pre"
        end = "</pre>"
        whois_answer = {}
        # get only the url, without the https://www.whois.com/whois/ prefix
        url = url[len("https://www.whois.com/whois/"):]

        # Do scraping if it exists, means the </pre> tag exists in the HTML
        if "</pre" in text:
            logging.debug('Pre exists')
            data = text[text.index(start) + len(start): text.index(end)]
            # Create key value pairs from the RAW WHOIS DATA part from the response
            for line in data.splitlines():
                line = line.split(":")
                if not line:  # empty line?
                    continue
                whois_answer[line[0]] = ' '.join(line[1:])

        # save the answere
        url_to_whois[url] = whois_answer

        # start the writing process
        logging.debug('Waiting for a lock')
        with self.lock2:
            try:
                logging.debug('Acquired a lock')
                logging.debug(
                    '###################################### WRITING ' + url + " data to file ######################################")
                do_parse2_writing(output_file_name, url_to_whois)
            finally:
                logging.debug('Released a lock')


def runThreadJob(semaphore, thread_pool, html_line, output_file, u_a, does_parse2_activated):
    logging.debug('Waiting to join the pool')
    with semaphore:
        name = threading.currentThread().getName()
        thread_pool.makeActive(name)
        if does_parse2_activated == 1:
            thread_pool.do_parse2(html_line, output_file, u_a)
        else:
            thread_pool.do_parse(html_line, output_file, u_a)
        thread_pool.makeInactive(name)


def append_ending_parse2_style(output_file_name, threads):
    # wait for all threads to finish their jobs
    for x in threads:
        x.join()

    # append things at the end of the json file
    with open(output_file_name, 'rb+') as filehandle:
        filehandle.seek(-2, os.SEEK_END)
        filehandle.truncate()
    with open(output_file_name, 'a') as filehandle:
        filehandle.write("\n]")


if __name__ == '__main__':
    """
        This code will send GET requests to the whois protocol server, parse the response, and save it as a Json file.
        This code works multithreaded . It send multithreaded requests to whois server, but only one writer are 
        able to write to the output file at the same time.
        
        :param input_file_name: containes the urls with "https://www.whois.com/whois/" prefix
        :param output_file_name: containes the whois data for each url in Json format. 
        :param does_parse2_activated: determines the Json writing style of the output_file  
        :return: Json file with the whois data as dictionaty for each url.

    """
    thread_pool = ThreadPool()
    semaphore = threading.Semaphore(100)
    does_parse2_activated = 0
    input_file_name = 'D:\Users\gelleral\Dropbox\Deutsche Telekom\\plain_urls.txt'
    output_file_name = 'D:\Users\gelleral\Dropbox\Deutsche Telekom\\plain_urls_ans.txt'
    with open(input_file_name, 'r') as inf, open(
            output_file_name, 'a') as outf:
        u_a = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.82 Safari/537.36"
        thread_counter = 0

        # check which style of parsing to activate
        if does_parse2_activated == 1:
            # append things at the begginning of the json file
            outf.write("[\n")
            outf.flush()

        threads = []
        for line in inf:
            thread_counter += 1
            thread = threading.Thread(target=runThreadJob, name='thread_' + str(thread_counter),
                                      args=(semaphore, thread_pool, line, output_file_name, u_a, does_parse2_activated))
            threads.append(thread)
            thread.start()

        # check which style of parsing to activate
        if does_parse2_activated == 1:
            append_ending_parse2_style(output_file_name, threads)
