import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from datetime import datetime
import re
from pathlib import Path

### GET ALL RELEVANT LINKS FROM PAGE ###

url = "https://www.zvg-online.net/1300/"
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")

# list of appendices of scheme: district_number/ag_seite_001
relevant_links_appendices = []
for link in soup.find_all("a"):
    if "ag_seite_001.php" in link.get("href"):
        relevant_links_appendices.append(link.get("href"))
#print(relevant_links_appendices)

# create list of concatened links of scheme url/district_number/ag_seite_001
relevant_links = []
for link in relevant_links_appendices:
    relevant_links.append(url+link)
# print(relevant_links)

# create a list where links are stored in regard to what district number they were taken from
district_link_list = []


# creates list of sets where each set contains appointments from that respective district
for site_link in relevant_links:
    # store links to individual appointment date with scheme: url/district_number/termin_n
    # set as to avoid having duplicates since links are placed multiple times on the website
    final_pages = set()
    page = requests.get(site_link)
    temp_soup = BeautifulSoup(page.content, "html.parser")
    for link in temp_soup.find_all("a"):
        if "termin" in link.get("href"):
            final_pages.add(site_link.removesuffix("ag_seite_001.php") + link.get("href"))
    district_link_list.append(final_pages)
#print(district_link_list)


### GETTING THE CONTENT/DATA ###

data_list = []
target_keywords = ["Grundstücksart:", "Objekt / Lage:", "Versteigerungsort:", "Zuständigkeit:"]

for district_set in district_link_list:
    district_links = list(district_set)
    for link in district_links:
        # store pairs in a dict
        temp_data_dict = {}

        target_url = link
        target_page = requests.get(target_url)
        target_soup = BeautifulSoup(target_page.content, "html.parser")

        # Find all <tr> tags
        tr_tags = target_soup.find_all('tr')

        # iterate over all tr tags
        for tr_tag in tr_tags:
            td_tags = tr_tag.find_all('td')
            # always two td tags are inside one tr tag of the target text
            if len(td_tags) == 2:
                key = td_tags[0].get_text().strip()

                # "Versteigerungstermin" is a special case where the date of the auction is inside a different tag
                if "Versteigerungstermin" in key:
                    key_split = key.split(":", 1)
                    key = key_split[0]
                    value = key_split[1]
                else:
                    value = td_tags[1].get_text().strip()

                # TODO remove trash from the dict
                if key in target_keywords:
                    temp_data_dict[key] = value

        # get the content of the description of the property
        body_text = []
        paragraphs = target_soup.find_all("p")
        for p in paragraphs:
            if "Versteigert wird" in p.get_text():
                # clean the string of clutter symbols
                cleaned_string = re.sub(r'\s+', ' ', p.get_text())
                body_text.append(cleaned_string)
        # if multiple texts remain, raise error
        if len(body_text) > 1:
            raise Exception("List is longer than 1 element!")
        else:
            temp_data_dict["Beschreibung"] = body_text[0]
        
        # matches the price 
        pattern = r"ermittelter Verkehrswert in EURO: ([\d.,]+)"
        match = re.search(pattern, body_text[0])
        # if price is found add it to the dict
        if match:
            value = match.group(1)
            temp_data_dict["ermittelter Verkehrswert in EURO:"] = value
        # if no price can be found enter NaN
        # TODO see if all properties have a price
        else:
            temp_data_dict["ermittelter Verkehrswert in EURO:"] = np.NaN
        data_list.append(temp_data_dict)


### OUTPUT THE DATA TO CSV ###
final_data = pd.DataFrame(data_list)

# get curretn date and time
current_datetime = datetime.now()
formatted = current_datetime.strftime('%Y-%m-%d_%H-%M-%S')

# creates output folder
folder_path = Path(f"output/data_{formatted}.csv")
folder_path.parent.mkdir(exist_ok=True, parents=True)

# saves data to csv, no index
final_data.to_csv(folder_path, sep=",", index=False)




### For testing
# print(final_data)