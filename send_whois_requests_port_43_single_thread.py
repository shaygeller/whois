import json
import logging
import multiprocessing
import time
from utils import *

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s', )

# Global variables
whois_servers_file_name = "D:\Users\gelleral\Dropbox\Deutsche Telekom\whois thigs\whois servers list.txt"
whois_servers = get_whois_server_list(whois_servers_file_name)

# tld_parse_functions = {".kr": parse_whois_response_kr,
#                        "default2": parse_whois_response_default2,
#                        "default": parse_whois_response_default}
whois_standard_dict = ["Domain Name", "Registrant Name", "Registrant City", "Registrant Country", "Name Server",
                       "Updated Date"]


def do_parse_writing(output_file_name, url_to_whois):
    with open(output_file_name, 'a') as outf:
        json.dump(url_to_whois, outf)
        outf.write('\n')


def do_parse2_writing(output_file_name, url_to_whois):
    with open(output_file_name, 'a') as outf:
        json.dump(url_to_whois, outf)
        outf.write(",")
        outf.write('\n')


def do_parse(line):
    """
    Thread execute job.
    This job will send http request for the whois server match to the LTD of the url in the line, and save the response in an output file.
    :param line: line with url address
    :param output_file_name: name for output file
    :param u_a: USER-AGENT, something for sending the requests
    :return: void
    """

    url_origin = line.strip()
    if url_origin.endswith("."):
        url_origin = url_origin[:-1]
    print "URL:" + url_origin
    data = get_whois_data(url_origin, whois_servers)
    whois_answer = {}
    for line in data.splitlines():
        if line.startswith("%") or ":" not in line:
            continue
        line = line.split(":")
        line[0] = line[0].strip()
        line[0] = check_rename_line_start(line[0])
        if line[0] in whois_answer:
            whois_answer[line[0]] = whois_answer[line[0]] + "," + ''.join(line[1:]).strip()
        elif "Registrant Address" in line[0]:
            print "try to change address to " + url_origin
            city, country = get_city_country_using_googlemapsapi(line[1:])
            if "Registrant City" not in whois_answer.keys():
                whois_answer["Registrant City"] = city
                whois_answer["Registrant Country"] = country
        else:
            whois_answer[line[0]] = ' '.join(line[1:]).strip()

    # save_ans_single_thread(url_origin, whois_answer, logging, do_parse_writing, output_file_name)
    return url_origin, whois_answer





if __name__ == '__main__':
    multiprocessing.freeze_support()
    start_time = time.time()

    """
        This code will send GET requests to the whois protocol server, parse the response, and save it as a Json file.
        This code works multithreaded . It send multithreaded requests to whois server, but only one writer are 
        able to write to the output file at the same time.

        :param input_file_name: containes the urls with "https://www.whois.com/whois/" prefix
        :param output_file_name: containes the whois data for each url in Json format. 
        :param does_parse2_activated: determines the Json writing style of the output_file  
        :return: Json file with the whois data as dictionaty for each url.

    """
    input_file_name = 'D:\Users\gelleral\Dropbox\Deutsche Telekom\\plain_urls.txt'
    output_file_name = 'D:\Users\gelleral\Dropbox\Deutsche Telekom\\' + time.strftime(
        "%Y_%m_%d") + '_plain_urls_ans.txt'
    with open(input_file_name, 'r') as inf, open(
            output_file_name, 'w') as outf:
        pool = multiprocessing.Pool(multiprocessing.cpu_count()*2)
        for result in pool.imap_unordered(do_parse, inf):
            url_to_whois = {result[0]: result[1]}
            json.dump(url_to_whois, outf)
            outf.write('\n')
        pool.close()
        print "My program took", time.time() - start_time, "to run"

        # for line in inf:
        #     result = do_parse(line)
        #     url_to_whois = {result[0]: result[1]}
        #     json.dump(url_to_whois, outf)
        #     outf.write('\n')
