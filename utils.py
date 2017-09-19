import socket
from random import randint

import googlemaps
import time

import re


def hasNumber(inputString):
    return bool(re.search(r'\d', inputString))


def getNumber(inputString):
    return re.search(r'\d', inputString).start()


def get_city_country_using_googlemapsapi(location):
    """
     Get city and country from location address using google api
    :param location:
    :return: city,country list
    """
    gmaps = googlemaps.Client(key='AIzaSyDlwd6RTElD-9FvGSSA7QE8AKBQR8WVfMY')
    location = "".join(location)
    # Geocoding an address
    first_digit_location = 0
    if hasNumber(location):
        first_digit_location = getNumber(location)
    location = location[first_digit_location:]
    result = gmaps.geocode(location)
    reverse_geocode_result = gmaps.reverse_geocode((40.714224, -73.961452))
    # print result
    city_num = 4
    country_num = 5
    city = ""
    country = ""
    counter = 0
    if len(result) < country_num:
        return ["Couldn't find city", "Couldn't find country"]
    for x in result[0]["address_components"]:
        counter = counter + 1
        if counter == city_num:
            city = x["long_name"]
        if counter == country_num:
            country = x["long_name"]
            break
    return [city, country]


def get_whois_server_list(file_name):
    """
    Get whois servers from a file
    :param file_name: whois servers file
    :return: dict of tld :whois_server data
    """
    whois_servers = {}
    with open(file_name) as f:
        for line in f:
            (key, val) = line.split()
            whois_servers[key] = val
    return whois_servers


# Perform a generic whois query to a server and get the reply
def perform_whois(server, query,requests_counter):
    """
     Perform a generic whois query to a server and get the reply

    :param server: name of the whois server
    :param query: name of the url to query
    :param requests_counter: counter of retries in case of an error
    :return: response from the whois server or "Finish loop of requests without response" which indicates a loop that
     ended without a good response
    """
    s = None
    msg = ""
    retries_num = 3
    if requests_counter == retries_num:
        print "Stop sending requests for " + query + " after " + str(requests_counter) + " attempts"
        msg = "Finish loop of requests without response"
        return msg
    try:
        # socket connection
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(30)
        # s.getaddrinfo('127.0.0.1', 80)
        s.bind(('', 0))
        # addr,port = s.getsockname()
        # print str(port) +"\n"
        s.connect((server, 43))

        # send data
        s.send(query + '\r\n')

        # receive reply
        # return s.recv()
        while len(msg) < 10000:
            chunk = s.recv(100)
            if chunk == '':
                break
            msg = msg + chunk
        s.close()
        return msg
    except Exception as e:
        # TODO: get all the tld with errors and fix them, 
        # TODO: get all the tld with errors and fix them,
        # TODO: create a test suit for thies problems
        print "Error: some socket problem, need to rerun the whois lookup, problem url is: " + query + " whois server is " + server
        print e
    finally:
        if s is not None:
            s.close()
        time.sleep(randint(1, 3))
    return perform_whois(server, query,requests_counter+1)


# Function to perform the whois on a domain name
def get_whois_data(domain, whois_servers):
    """
        Function to perform the whois on a domain name
    :param domain: domain name to query
    :param whois_servers: dict of all the whois server (tld:whois_server records)
    :return: The response from the whois server, or empty if no response or not a valid url
    """
    # remove http and www
    domain = domain.replace('http://', '')
    domain = domain.replace('www.', '')

    # get the extension , .com , .org , .edu
    if "." in domain:
        tld = get_tld(domain)
        print "Domin is: " + domain + ",    Tld is " + tld
        # if "." not in tld: #means TLD like com,net,org
        if tld in whois_servers:
            whois = whois_servers[tld]
        else:
            whois = 'whois.internic.net'
        if "tr" is tld: # .tr tld doesnt work with whois requests TODO: check why tr tld not working with whois requests
            return "";

        msg = perform_whois(whois, domain,0)
    else:  # no TLD in the url, not a valid url
        msg = ""  # Return the reply
    return msg


def get_tld(url):
    """
     Returns the TLD of a given url
    :param url: url
    :return: TLD which is a string starts with dot.
    """
    if (url.endswith(".")):
        url = url[:-1]
    return url[str(url).rfind(".")+1:]


#
# ci, cou = get_city_country_using_googlemapsapi('22nd Floor Gangnam Finance Center 737, Yeoksam-dong Kangnam-ku Seoul')
# print ci
# print cou
#

def parse_whois_response_default(response, url_origin, logging, self, do_parse_writing, output_file_name):
    # Start the scrapper
    start = "<pre"
    end = "</pre>"
    whois_answer = {}
    # get only the url, without the https://www.whois.com/whois/ prefix
    url_for_whois_requests = url_origin

    # Do scraping if whois data exists, means the </pre> tag exists in the HTML
    if "</pre" in response:
        logging.debug('Pre exists')
        data = response[response.index(start) + len(start): response.index(end)]
        # Create key value pairs from the RAW WHOIS DATA part from the response
        for line in data.splitlines():
            line = line.split(":")
            line[0] = line[0].strip()
            line[0] = check_rename_line_start(line[0])
            if not line:  # empty line?
                continue
            if line[0] in whois_answer:
                whois_answer[line[0].strip()] = whois_answer[line[0]] + "," + ''.join(line[1:]).strip()
            else:
                whois_answer[line[0].strip()] = ' '.join(line[1:]).strip()
    save_ans(url_for_whois_requests, whois_answer, logging, self, do_parse_writing, output_file_name)


def parse_whois_response_default2(response, url_origin, logging, self, do_parse_writing, output_file_name):
    # Start the scrapper
    start = "<div class=\"raw well well-sm\">"
    end = "<div class=\"col-md-4 col-sm-4\">"
    whois_answer = {}
    # get only the url, without the https://www.whois.com/whois/ prefix
    url_for_whois_requests = url_origin

    # Do scraping if whois data exists, means the </pre> tag exists in the HTML
    if start in response:
        logging.debug('Pre exists')
        data = response[response.index(start) + len(start): response.index(end)]
        # Create key value pairs from the RAW WHOIS DATA part from the response
        for line in data.splitlines():
            line = line.split(":")
            line[0] = line[0].strip()
            line[0] = check_rename_line_start(line[0])
            if not line:  # empty line?
                continue
            if line[0] in whois_answer:
                whois_answer[line[0].strip()] = whois_answer[line[0]] + "," + ''.join(line[1:]).strip()
            else:
                whois_answer[line[0].strip()] = ' '.join(line[1:]).strip()
    save_ans(url_for_whois_requests, whois_answer, logging, self, do_parse_writing, output_file_name)


def save_ans(url_for_whois_requests, whois_answer, logging, self, do_parse_writing, output_file_name):
    """
        Save the answere to Json file
        Create Json object like this:
            [
              {"string":"string1","int":1,"array":[1,2,3],"dict": {"key": "value1"}},
              {"string":"string2","int":2,"array":[2,4,6],"dict": {"key": "value2"}},
              {"string":"string3","int":3,"array":[3,6,9],"dict": {"key": "value3", "extra_key": "extra_value3"}}
            ]

    """
    url_to_whois = {}
    url_to_whois[url_for_whois_requests] = whois_answer

    # start the writing process
    logging.debug('Waiting for a lock')
    with self.lock2:
        try:
            logging.debug('Acquired a lock')
            logging.debug(
                '###################################### WRITING ' + url_for_whois_requests + " data to file ######################################")
            do_parse_writing(output_file_name, url_to_whois)
        finally:
            logging.debug('Released a lock')


def save_ans_single_thread(url_for_whois_requests, whois_answer, logging, do_parse_writing, output_file_name):
    """
        Save the answere to Json file
        Create Json object like this:
            [
              {"string":"string1","int":1,"array":[1,2,3],"dict": {"key": "value1"}},
              {"string":"string2","int":2,"array":[2,4,6],"dict": {"key": "value2"}},
              {"string":"string3","int":3,"array":[3,6,9],"dict": {"key": "value3", "extra_key": "extra_value3"}}
            ]

    """
    url_to_whois = {}
    url_to_whois[url_for_whois_requests] = whois_answer

    # start the writing process
    logging.debug('Waiting for a lock')
    try:
        logging.debug('Acquired a lock')
        logging.debug(
            '###################################### WRITING ' + url_for_whois_requests + " data to file ######################################")
        do_parse_writing(output_file_name, url_to_whois)
    finally:
        logging.debug('Released a lock')


def check_rename_line_start(line_start):
    if "Host Name" in line_start:
        return "Name Server"
    elif "Last Updated Date" in line_start:
        return "Update Date"
    elif "Registered Date" in line_start:
        return "Creation Date"
    elif "Updated Date" in line_start:
        return "Update Date"
    else:
        return line_start


def parse_whois_response_kr(response, url_origin, logging, self, do_parse_writing, output_file_name):
    start = "# ENGLISH<br>"
    end = "- KISA/KRNIC WHOIS Service -"
    whois_answer = {}
    # get only the url, without the https://www.whois.com/whois/ prefix
    url_for_whois_requests = url_origin
    data = response[response.index(start) + len(start): response.index(end)].strip()
    data = data.replace("<br>", "").strip()
    # Do scraping if whois data exists, means the </pre> tag exists in the HTML
    # logging.debug(str(response))
    if "The requested Host was not found" not in data:
        logging.debug('whois data exists')
        # TODO: Fix this data variable
        # Create key value pairs from the RAW WHOIS DATA part from the response
        for line in data.splitlines():
            line = line.split(":")
            line[0] = line[0].strip()
            line[0] = check_rename_line_start(line[0])
            if not line or len(line) == 1:  # empty line?
                continue
            if line[0] in whois_answer:
                whois_answer[line[0]] = whois_answer[line[0]] + "," + ''.join(line[1:]).strip()
            elif "Registrant Address" in line[0]:
                city, country = get_city_country_using_googlemapsapi(line[1:])
                whois_answer["Registrant City"] = city
                whois_answer["Registrant Country"] = country
            else:
                whois_answer[line[0]] = ' '.join(line[1:]).strip()
    save_ans(url_for_whois_requests, whois_answer, logging, self, do_parse_writing, output_file_name)
