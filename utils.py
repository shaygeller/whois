import socket

import errno
import googlemaps
from datetime import datetime

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
        return ["Couldn't find city","Couldn't find country"]
    for x in result[0]["address_components"]:
        counter = counter + 1
        if counter == city_num:
            city = x["long_name"]
        if counter == country_num:
            country = x["long_name"]
            break
    return [city, country]


def get_whois_server_list(file_name):
    whois_servers = {}
    with open(file_name) as f:
        for line in f:
            (key, val) = line.split()
            whois_servers[key] = val
    return whois_servers


# Perform a generic whois query to a server and get the reply
def perform_whois(server, query):
    s = None
    try:
        # socket connection
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(30)
        # s.bind(('', 0))
        # addr,port = s.getsockname()
        # print str(port) +"\n"
        s.connect((server, 43))

        # send data
        s.send(query + '\r\n')

        # receive reply
        # return s.recv()
        msg = ''
        while len(msg) < 10000:
            chunk = s.recv(100)
            if chunk == '':
                break
            msg = msg +chunk

        return msg
    except Exception as e:
        print "Error: some socket problem, need to rerun the whois lookup"
        print e
    finally:
        if s is not None:
            s.close()

    perform_whois(server, query)

# End

# Function to perform the whois on a domain name
def get_whois_data(domain, whois_servers):
    # remove http and www
    domain = domain.replace('http://', '')
    domain = domain.replace('www.', '')

    # get the extension , .com , .org , .edu
    ext = domain[-3:]

    # If top level domain .com .org .net
    if (ext == 'com' or ext == 'org' or ext == 'net'):
        # whois = 'whois.internic.net'
        if ext in whois_servers:
            whois = whois_servers[ext]
        else:
            whois = 'whois.internic.net'
        msg = perform_whois(whois, domain)

        # Now scan the reply for the whois server
        lines = msg.splitlines()
        for line in lines:
            if ':' in line:
                words = line.split(':')
                if 'Whois' in words[0] and 'whois.' in words[1]:
                    whois = words[1].strip()
                    break;

    # Or Country level - contact whois.iana.org to find the whois server of a particular TLD
    else:
        # Break again like , co.uk to uk
        ext = domain.split('.')[-1]

        # This will tell the whois server for the particular country
        # whois = 'whois.iana.org'
        if ext in whois_servers:
            whois = whois_servers[ext]
        else:
            whois = 'whois.internic.net'
        msg = perform_whois(whois, ext)

        # Now search the reply for a whois server
        lines = msg.splitlines()
        for line in lines:
            if ':' in line:
                words = line.split(':')
                if 'whois.' in words[1] and 'Whois Server (port 43)' in words[0]:
                    whois = words[1].strip()
                    break;

    # Now contact the final whois server
    msg = perform_whois(whois, domain)

    # Return the reply
    return msg


def get_tld(url):
    """
     Returns the TLD of a given url
    :param url: url
    :return: TLD which is a string starts with dot.
    """
    if (url.endswith(".")):
        url = url[:-1]
    return url[str(url).rfind("."):]


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
