import csv
import json

# Put here the wanted element names from the whois data.
# You can see the RAW WHOIS DATA section in this site for example: https://www.whois.com/whois/www.rphilsdanceteam.com.
# Notice! not all RAW WHOIS DATA are the same, but most of them does.
whois_wanted_elements = ["Tech Email", "Creation Date", "Updated Date", "Registrant Country"]
stats_elements = ["Total number of urls", "Has whois data"] + whois_wanted_elements
stats = {key:0 for key in stats_elements}
# stats = dict.fromkeys(whois_wanted_elements)
# for s in stats:
#     stats[s] = 0;

# Iterate over the whois data json, and locate the whois_wanted_elements for each url in the whois data json.

input_file_name = 'D:\Users\gelleral\Dropbox\Deutsche Telekom\\text.txt'
output_file_name = 'D:\Users\gelleral\Dropbox\Deutsche Telekom\url_to_whois.csv'
with open(input_file_name, 'r+') as urls_file, \
    open(output_file_name, "ab") as csv_file:
    # Add schema to csv
    first_schema_line = ["URL"] + whois_wanted_elements
    writer = csv.writer(csv_file, delimiter=',')
    writer.writerow(first_schema_line)

    for line in urls_file:
        # transform a line into a python dict
        dict_as_json = json.loads(line)
        url_dict = dict(dict_as_json)

        stats["Total number of urls"] += 1

        for url in url_dict:
            csv_line = []
            csv_line.append(url)
            for whois_data_element in url_dict[url]:
                if whois_data_element in whois_wanted_elements:
                    stats[whois_data_element] +=1
                    csv_line.append(url_dict[url][whois_data_element])
                # print whois_data_element + ":" + url_dict[url][whois_data_element]

            if len(csv_line) > 1:
                stats["Has whois data"] +=1
            # Writing a line of data to csv file
            writer = csv.writer(csv_file, delimiter=',')
            writer.writerow(csv_line)

# print stats
for s in stats:
    print s + ":" + str(stats[s])


# TODO: Clean HTML image tag from Registrant email address
# TODO: add support for the DENIC whois data provider (for urls with .de ending)