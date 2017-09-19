import json

import requests
from HTMLParser import HTMLParser

# with open('D:\Users\gelleral\Dropbox\Deutsche Telekom\url_with_infix.txt','r') as inf, open('D:\Users\gelleral\Dropbox\Deutsche Telekom\\text.txt', 'w') as outf:
with open('d:\Users\gelleral\Desktop\\10.txt','r') as inf, open('D:\Users\gelleral\Dropbox\Deutsche Telekom\\text.txt', 'w') as outf:
    url_to_whois = {}
    u_a = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.82 Safari/537.36"
    counter = 0
    for line in inf:
        counter = counter + 1
        print counter
# url = 'https://www.whois.com/whois/google.com'
        url = line.strip()
        r = requests.get(url, headers={"USER-AGENT":u_a})
# r = requests.get('https://www.whois.com/whois/google.com', auth=('user', 'pass'))

# r.status_code
# print r.headers['Transfer-Encoding']
# print r.encoding
# print r.text.decode('utf-8')

        # get the HTML text from the response
        text = r.text  #.decode('utf-8')

        # The raw HTML for debug purposes
        raw_start = "<div class=\"whois_main_column\">"
        raw_end = "<div class=\"whois_rhs_column\">"
        rawHtml = text[text.index(raw_start)+len(raw_start): text.index(raw_end)]
        print rawHtml
        # Start the scrapper
        start = "<pre"
        end = "</pre>"
        whois_answer = {}
        whois_answer["sourceURL"] = url
        whois_answer["sourceURLrawHTML"] = rawHtml
        url_to_whois[url] = whois_answer

        # Do scraping if it exists, means the </pre> tag exists in the HTML
        if "</pre" in text:
            data = text[text.index(start)+len(start): text.index(end)]
            for line in data.splitlines():
                line = line.split(":")
                if not line:  # empty line?
                    continue
                whois_answer[line[0]] = ' '.join(line[1:])
            #save the answere
            url_to_whois[url] = whois_answer
            json.dump(url_to_whois, outf)

    # json.dump(url_to_whois, outf)


# for i in answer:
    # print i + ":" + answer[i]


