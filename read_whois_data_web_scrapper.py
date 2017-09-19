import csv
# import json
import simplejson as json
from dateutil.parser import parse
# Put here the wanted element names from the whois data.
# You can see the RAW WHOIS DATA section in this site for example: https://www.whois.com/whois/www.rphilsdanceteam.com.
# Notice! not all RAW WHOIS DATA are the same, but most of them does.
whois_wanted_elements = ["Update Date", "Creation Date","Admin City", "Admin Country","Name Server", "Registrant Name","Registrant","Registrant Country","Registrant City"]
whois_wanted_elements = sorted(whois_wanted_elements)
stats_elements = ["Total number of urls", "Has whois data"] + whois_wanted_elements
stats = {key:0 for key in stats_elements}
# Iterate over the whois data json, and locate the whois_wanted_elements for each url in the whois data json.

input_file_name = 'D:\Users\gelleral\Dropbox\Deutsche Telekom\\2017_09_12_plain_urls_ans.txt'
output_file_name = input_file_name[:-4] + "_parsed.csv"
with open(input_file_name, 'r+') as urls_file, \
    open(output_file_name, "ab") as csv_file:
    # Add schema to csv
    first_schema_line = ["URL"] + whois_wanted_elements
    writer = csv.writer(csv_file, delimiter=',')
    writer.writerow(first_schema_line)
    counter = 0;
    for line in urls_file:
        # transform a line into a python dict
        # line = line.encode('utf-8')
        line = line.encode('ascii', 'ignore').decode('ascii')
        dict_as_json = json.loads(line)
        url_dict = dict(dict_as_json)
        print counter
        counter+=1
        stats["Total number of urls"] += 1

        for url in url_dict:
            csv_line = []
            csv_line.append(url)
            has_whois_data = False
            for element in whois_wanted_elements:
                print "ELEMENT is "  +element
                if element in url_dict[url].keys():
                    has_whois_data = True
                    elem = url_dict[url][element].strip()
                    print "elem " + elem
                    print "url " + url
                    print "ELEMENT : "+ element + " for the url " + url
                    if elem is not "" and element in ["Creation Date","Updated Date"]:
                        if len(elem) < 2:
                            # element is too short
                            elem = ""
                            print "TOO SHORT ################################################################################"
                        elif " " in elem and len(elem) > 2:
                            elem_list = elem.split(" ")
                            elem_temp = max(elem_list, key=len)
                            print "elem_temp " + elem_temp
                            print "Len is " + str(len(elem_temp))
                            if "GMT" in str(elem_temp):
                                elem_temp = elem_list[1] + " " + elem_list[2] + " " + elem_list[3]
                            elif len(elem_temp) < 7:
                                elem_temp = elem_list[0]+ " " +elem_list[1] +" "+ elem_list[2]
                            elif str(elem_temp).count("-") == 2 or str(elem_temp).count("/") == 2 or str(elem_temp).count(".") == 2:
                                elem_temp = elem_temp
                            #
                            elif len(elem_temp) ==8:
                                elem_temp = elem_temp[0:4] + "/" + elem_temp[4:6] + "/" + elem_temp[6:]
                            # elif len(elem_temp) is 10:
                            #     elem_temp = elem_temp
                            elif "+" in elem_temp:
                                elem_temp = elem_list[0]
                            elif len(elem_temp) is 13:
                                elem_temp = elem_temp[:10]
                                if elem_temp.startswith("-"):
                                    elem_temp = str(elem_temp).replace("-","2",1)
                                    print "replaced element is " + elem_temp
                                print "elem_temp " + elem_temp
                            elif len(elem_temp) is 14:
                                elem_temp = elem_temp[:10]
                                if elem_temp.startswith("-"):
                                    elem_temp = str(elem_temp).replace("-","2",1)
                                    print "replaced element is " + elem_temp
                                print "elem_temp " + elem_temp
                            else:
                                elem_temp = elem_list[0] + " " +elem_list[1] +" "+ elem_list[2]
                                print "else case " + elem_temp
                            elem = elem_temp
                            print "Final elem " + elem
                            if "0000-00-00" in elem :
                                elem = ""
                                continue
                            try:
                                elem = parse(elem)
                            except Exception:
                                print "Cant parse " + elem
                            finally:
                                if len(str(elem)) < 1:
                                    elem = ""

                            try:
                                elem = elem.strftime('%d/%m/%Y')
                            except Exception:
                                print "Cant Eval " + elem
                            finally:
                                if len(elem) < 1:
                                    elem = ""

                            print "Date is " + elem

                    stats[element] += 1
                    csv_line.append(elem)
                else:
                    csv_line.append("")
            if has_whois_data:
                stats["Has whois data"] +=1
            # Writing a line of data to csv file
            writer = csv.writer(csv_file, delimiter=',')
            # writer.writerow(csv_line)
            writer.writerow([unicode(s).encode("utf-8") for s in csv_line])

# print stats
for s in stats:
    print s + ":" + str(stats[s])


# TODO: Clean HTML image tag from Registrant email address
# TODO: add support for the DENIC whois data provider (for urls with .de ending)