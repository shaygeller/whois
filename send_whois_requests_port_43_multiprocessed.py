import json
import logging
import multiprocessing
import os
import time
from utils import *

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s', )

# Global variables
whois_servers_file_name = os.path.join("data","whois_servers_list.txt")
whois_servers = get_whois_server_list(whois_servers_file_name)
# print whois_servers
whois_standard_dict = ["Domain Name", "Registrant Name", "Registrant City", "Registrant Country", "Name Server",
                       "Updated Date"]

def do_parse(line):
    """
    Thread execute job.
    This job will send http request for the whois server match to the LTD of the url in the line, and save the response in an output file.
    :param line: line with url address
    :param output_file_name: name for output file
    :param u_a: USER-AGENT, something for sending the requests
    :return: void
    """
    start_time_do_parse = time.time()
    # TODO: create Clean url function to be used everywhere
    url_origin = line.strip()
    if url_origin.endswith("."):
        url_origin = url_origin[:-1]
    # print "URL:" + url_origin
    data = get_whois_data(url_origin, whois_servers)
    whois_answer = {}
    if "Finish loop of requests without response" in data:
        # Means the whois server blocking the requests due to too many continuous requests
        # So we will return spacific whois_answar to inform about it
        whois_answer["error_loop"] = data
        return url_origin, whois_answer
    if data.startswith("NOT FOUND") or data.startswith("No match for") or data.startswith("No data found") or (
                "No entries found for the selected source" in data):
        return url_origin, whois_answer
    for line in data.splitlines():
        if line.startswith("%") or ":" not in line:
            continue
        line = line.split(":")
        line[0] = line[0].strip()
        line[0] = check_rename_line_start(line[0])
        # TODO: Think of better way to represent the concatination
        if line[0] in whois_answer:
            whois_answer[line[0]] = whois_answer[line[0]] + "," + ''.join(line[1:]).strip()
        elif "Registrant Address" in line[0]:
            print "try to change address to " + url_origin
            city, country = get_city_country_using_googlemapsapi(line[1:])
            if "Registrant City" not in whois_answer.keys():
                whois_answer["Registrant City"] = city
            if "Registrant Country" not in whois_answer.keys():
                whois_answer["Registrant Country"] = country
        # elif len(whois_answer.keys()) == 0 and "TERMS OF USE" in line[0]:
        #     #means no whois data in the response from the whois server
        #     whois_answer = {}
        else:
            whois_answer[line[0]] = ' '.join(line[1:]).strip()

    print "Url " + url_origin + " parsing time: ", time.time() - start_time_do_parse, "to run"
    return url_origin, whois_answer


if __name__ == '__main__':
    """
    This code will run whois requests on a list of urls and return a file that each line in it is a
    dictionary of the whois response for a single url  
    :param input_file_name: file of urls to perform whois queries on
    :param output_file_name: output file name for the whois responses
    :param empty_results_file_name: file name that will contain the url that there was no response for them in the loop
    :param chunk_size: number of lines for each process to handle
    :param retries_num: number of whosi retries in case fo an error 
    :param mul_of_processors: number to multiply the number of cores in the CPU
    :return: void
    """
    # TODO: Add all vatriabels to configuration file  (ConfigParser class)
    multiprocessing.freeze_support()
    chunk_size = 2
    mul_of_processors = 2
    # TODO: wrap the do_parse func to insert the retries_num as a parameter in that function
    retries_num = 3
    start_time = time.time()
    # input_file_name = os.path.join("data","1k_urls.txt")
    input_file_name = os.path.join("data","1k_urls.txt")
    output_file_name = os.path.join("results",time.strftime("%Y_%m_%d") + "_urls_ans.txt")
    empty_results_file_name = os.path.join("results",time.strftime("%Y_%m_%d") + "_error_urls_ans.txt")


    with open(input_file_name, 'r') as inf, open(output_file_name, 'wb') as outf, open(
        empty_results_file_name, 'wb') as empty_f:
        pool = multiprocessing.Pool(multiprocessing.cpu_count() * mul_of_processors)
        for result in pool.imap(do_parse, inf, chunk_size):
            try:
                # print "writing " + result[0] + ", the data is\n" +result[1]
                url_to_whois = {result[0]: result[1]}
                if "error_loop" in result[1].keys():  # empty dict is false
                    # Save empty result in a seperate file
                    print "Socket loop returned empty result in " + str(result[0])
                    empty_f.write(str(result[0]) + "\n")
                    # empty_f.flush()
                json.dump(url_to_whois, outf)

                outf.write('\n')
            except Exception as e:
                print "Error in " + result[0]
                print "the data is:\n" + str(result[1])
                print e

        pool.close()
        print "My program took", time.time() - start_time, "to run, chunk size: " + str(chunk_size)

        # for line in inf:
        #     result = do_parse(line)
        #     url_to_whois = {result[0]: result[1]}
        #     json.dump(url_to_whois, outf)
        #     outf.write('\n')


# TODO: Change the empty results name
# TODO: instead print do log4j
# TODO: Change names to os.path....
# TODO: Split the code into logic and presentation folders