import googlemaps
from datetime import datetime



def get_city_country_using_googlemapsapi(location):
    """
     Get city and country from location address using google api
    :param location:
    :return: city,country list
    """
    gmaps = googlemaps.Client(key='AIzaSyDlwd6RTElD-9FvGSSA7QE8AKBQR8WVfMY')
    # Geocoding an address
    result = gmaps.geocode(location)
    reverse_geocode_result = gmaps.reverse_geocode((40.714224, -73.961452))
    # print result
    city_num = 4
    country_num = 5
    city = ""
    country = ""
    counter = 0
    for x in result[0]["address_components"]:
        counter = counter + 1
        if counter == city_num:
            city = x["long_name"]
        if counter == country_num:
            country = x["long_name"]
    return [city,country]


def get_tld(url):
    """
     Returns the TLD of a given url
    :param url: url
    :return: TLD which is a string starts with dot.
    """
    if (url.endswith(".")):
        url = url[:-1]
    return url[str(url).rfind("."):]


ci, cou = get_city_country_using_googlemapsapi('22nd Floor Gangnam Finance Center 737, Yeoksam-dong Kangnam-ku Seoul')
print ci
print cou


def parse_whois_response_default(response, url_origin,logging,self,do_parse_writing,output_file_name):
    url_to_whois = {}
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
            if not line:  # empty line?
                continue
            if line[0] in whois_answer:
                whois_answer[line[0].strip()] = whois_answer[line[0]] + "," + ''.join(line[1:]).strip()
            else:
                whois_answer[line[0].strip()] = ' '.join(line[1:]).strip()

    # save the answere
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

    """
        Create Json object like this:
            [
              {"string":"string1","int":1,"array":[1,2,3],"dict": {"key": "value1"}},
              {"string":"string2","int":2,"array":[2,4,6],"dict": {"key": "value2"}},
              {"string":"string3","int":3,"array":[3,6,9],"dict": {"key": "value3", "extra_key": "extra_value3"}}
            ]

    """


def parse_whois_response_kr(response, url_origin,logging,self,do_parse_writing,output_file_name):
    url_to_whois = {}
    logging.debug("LALA")
    start = "<pre"
    end = "</pre>"
    whois_answer = {}
    # get only the url, without the https://www.whois.com/whois/ prefix
    url_for_whois_requests = url_origin

    # Do scraping if whois data exists, means the </pre> tag exists in the HTML
    # logging.debug(str(response))
    if "The requested Host was not found" not in response:
        logging.debug('whois data exists')
        # TODO: Fix this data variable
        data = response[response.index(start) + len(start): response.index(end)]
        # Create key value pairs from the RAW WHOIS DATA part from the response
        for line in data.splitlines():
            line = line.split(":")
            line[0] = line[0].strip()
            print "LINE: " + line[0]
            if not line:  # empty line?
                continue
            if line[0] in whois_answer:
                whois_answer[line[0]] = whois_answer[line[0]] + "," + ''.join(line[1:]).strip()
            elif line[0] is "Registrant Address":
                city, country = get_city_country_using_googlemapsapi(line[1:])
                whois_answer["Registrant City"] = city
                whois_answer["Registrant Country"] = country
                print "IM HEREEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE"
            else:
                whois_answer[line[0]] = ' '.join(line[1:]).strip()

    # save the answere
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

    """
        Create Json object like this:
            [
              {"string":"string1","int":1,"array":[1,2,3],"dict": {"key": "value1"}},
              {"string":"string2","int":2,"array":[2,4,6],"dict": {"key": "value2"}},
              {"string":"string3","int":3,"array":[3,6,9],"dict": {"key": "value3", "extra_key": "extra_value3"}}
            ]

    """