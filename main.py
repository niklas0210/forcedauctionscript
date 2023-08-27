import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

url = "https://www.zvg-online.net/1300/"
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")

relevant_links_appendices = []
for link in soup.find_all("a"):
    if "ag_seite_001.php" in link.get("href"):
        relevant_links_appendices.append(link.get("href"))
#print(relevant_links_appendices)

relevant_links = []
for link in relevant_links_appendices:
    relevant_links.append(url+link)
#print(relevant_links)

extensions = []
final_pages = set()

for site_link in relevant_links:
    page = requests.get(site_link)
    temp_soup = BeautifulSoup(page.content, "html.parser")
    for link in temp_soup.find_all("a"):
        if "termin" in link.get("href"):
            final_pages.add(site_link.removesuffix("ag_seite_001.php") + link.get("href"))

print(final_pages)

table = pd.DataFrame(columns=["ID", "type", "location", "auction_location", "auction_date", "auction_time", "price", "link"])

price_list = []

for object in final_pages:
    object_page = requests.get(object)
    temp_soup_ad = BeautifulSoup(object_page.content, "html.parser")
    temp_title = temp_soup_ad.find("title").text
    temp_body = temp_soup_ad.find(align="justify").text
    ID = re.findall(str(re.escape("Aktenzeichen :"))+"(.*)"+str(re.escape(" für")),temp_title)[0]
    object_type = re.findall(str(re.escape("Zwangsversteigerung "))+"(.*)"+str(re.escape(": ")),temp_title)[0]
    location = re.findall(str(re.escape(": "))+"(.*)"+str(re.escape(" mit dem Aktenzeichen")),temp_title)[0]
    auction_location = re.findall(str(re.escape("für das "))+"(.*)"+str(re.escape(" im Bundesland")),temp_title)[0]
    #auction_date =
    #auction_time =
    price = re.findall(str(re.escape("ermittelter Verkehrswert in EURO: "))+"(.*)"+str(re.escape(" ")),temp_body)[0]
    #table.loc[ID] = [object_type, location, auction_location, auction_date, auction_time, price, object]

print(price_list)



#print(table)