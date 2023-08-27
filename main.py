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

table = pd.DataFrame(columns=["ID", "type", "location", "auction_location", "auction_date", "price", "link"])


ID_list = []
type_list = []
object_location_list = []
auction_location_list = []
auctiondate_list = []
price_list = []


for object in final_pages:
    object_page = requests.get(object)
    temp_soup_ad = BeautifulSoup(object_page.content, "html.parser")
    temp_title = temp_soup_ad.find("title").text
    temp_paragraph = temp_soup_ad.find("p", align="justify").text

    ID = re.findall(str(re.escape("Aktenzeichen :"))+"(.*)"+str(re.escape(" für")),temp_title)[0]
    object_type = re.findall(r"Zwangsversteigerung (.*?):", temp_title)
    object_location = re.findall(str(re.escape(": "))+"(.*)"+str(re.escape(" mit dem Aktenzeichen")),temp_title)[0]


    auction_location = re.findall(r"im (.*?), ", temp_paragraph) in
    auction_date = temp_paragraph.splitlines()[1]
    price = temp_paragraph.splitlines()[-1]
    if " €" or " Euro" in price:
        price.replace(" €", "")
        price.replace(" Euro", "")

    #list check
    ID_list.append(ID)
    type_list.append(object_type)
    object_location_list.append(object_location)
    auction_location_list.append(auction_location)
    auctiondate_list.append(auction_date)
    price_list.append(price)
    print(temp_paragraph)
    #table.loc[ID] = [object_type, object_location, auction_location, price, object]



#print(f"ID-Liste:{ID_list}") #klappt
#print(f"Type-Liste:{type_list}") #klappt
#print(f"Inseratsort-Liste:{object_location_list}") #klappt
#print(f"Auktionsort-Liste:{auction_location_list}") #noch machen
#print(f"Auktionsdatum-Liste:{auctiondate_list}") #klappt
#print(f"Preisliste{price_list}") #klappt, wobei Euro und Eurozeichen noch rausmüssen
