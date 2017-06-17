import bs4
import requests
import string
import re
import csv
import json

num = 0
#Text file containing University name, league, and roster URL
f_read = open("sites.txt", "rt")
data = []
#Dictionary variable containing individual player data, which is then transcribed to JSON
player_data = dict()

#Create single JSON output file
total_output = open("final_player_data.json", "w")

#CSV object of University text file
reader = csv.reader(f_read)

#Iterates through each University included in the original text file
for indx_0, line in enumerate(reader):
    #HTTP request to roster URL
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0)'}
    page = requests.get(line[2].strip(), headers = headers)
    #Create Beautiful Soup object out of the fetched HTML
    page.raise_for_status()
    soup = bs4.BeautifulSoup(page.content, "html.parser")

    #Optional, write pretty HTML to text file
    #html_file = open("html/{}.txt".format(line[0]), "w")
    #html_file.write(soup.prettify())

    #Create JSON file with University as title, within the roster subfolder
    #output_file = open("roster/{}.json".format(line[0]), "w")
            #Write a player's University and League to dictionary variable
    player_data['school'] = line[0].strip()
    player_data['league'] = line[1].strip()

    #Find all HTML table rows in the Beautiful Soup object
    trs = soup.find_all("tr")

    #Iterate over each HTML table row
    for tr in trs:
        #Find all HTML table data cells
        tds = tr.find_all("td")
        #Iterate over each table data cell
        for td in tds:
                #RegEx to find 3 numeric digits in a stripped table data cell
                weight_match = re.search(r'^\d{3}$', td.get_text().replace("\n", "").replace("\t", "").strip())
                #Finds height (e.g. 6-2 or 5-11)
                height_match = re.search(r'^(\d)-(\d{1,2})$', td.get_text().replace("\n", "").replace("\t", "").strip())
                #Looks for variations on University class standing
                fr_year = re.search(r'fr\.$|Fr\.$|fr$|Fr$|^freshman$|^Freshman$', td.get_text().replace("\n", "").replace("\t", "").strip())
                so_year = re.search(r'so\.$|So\.$|so$|So$|^sophomore$|^Sophomore$', td.get_text().replace("\n", "").replace("\t", "").strip())
                jr_year = re.search(r'jr\.$|Jr\.$|jr$|Jr$|^junior$|^Junior$', td.get_text().replace("\n", "").replace("\t", "").strip())
                sr_year = re.search(r'sr\.$|Sr\.$|Sr$|Sr$|^Senior$|^Senior$', td.get_text().replace("\n", "").replace("\t", "").strip())
                #Looks for variations on Lacrosse positions
                a_pos = re.search(r'a$|A$|Attack$|attack$', td.get_text().replace("\n", "").replace("\t", "").strip())
                d_pos = re.search(r'd$|D$|Defense$|defense$', td.get_text().replace("\n", "").replace("\t", "").strip())
                g_pos = re.search(r'g$|G$|GK$|Gk$|gk$|Goalie$', td.get_text().replace("\n", "").replace("\t", "").strip())
                m_pos = re.search(r'm$|M$|Middie$|middie$', td.get_text().replace("\n", "").replace("\t", "").strip())
                lsm_pos = re.search(r'LSM$|lsm$', td.get_text().replace("\n", "").replace("\t", "").strip())
                #am_pos = re.search(r'A\/M$|a\/m$\M\/A$|m\/a$', td.get_text().replace("\n", "").replace("\t", "").strip())
                fo_pos = re.search(r'F\/O|Face-off$|Face-Off$|FO$|FO\/M$|M\/FO$', td.get_text().replace("\n", "").replace("\t", "").strip())

                #Reads in variations on State names and abbreviations from a CSV file
                f_state = open("states.txt", "rt")
                states = csv.reader(f_state)
                for state in states:
                        for name in state:
                                #Looks for State name or abbreviation in stripped table data cell
                                state_check = None
                                state_check = re.search(r', ' + re.escape(name), td.get_text().replace("\n", "").replace("\t", "").strip())
                                if state_check:
                                    player_data['state'] = state[0]

                #If/Elif checks if the RegEx search method returned true, and if so, assigns a specific data variable directly from the tabledata cell or assigns a predetermined string
                if weight_match:
                        player_data['weight'] = td.get_text().replace("\n", "").replace("\t", "").strip()
                elif height_match:
                        feet = int(height_match.group(1))
                        inches = int(height_match.group(2))
                        total_height = (feet * 12) + inches
                        player_data['height'] = str(total_height)
                elif fr_year:
                        player_data['year'] = 'freshman'
                elif so_year:
                        player_data['year'] = 'sophomore'
                elif jr_year:
                        player_data['year'] = 'junior'
                elif sr_year:
                        player_data['year'] = 'senior'
                elif a_pos:
                        player_data['position'] = 'attack'
                elif d_pos:
                        player_data['position'] = 'defense'
                elif g_pos:
                        player_data['position'] = 'goalie'
                elif m_pos:
                        player_data['position'] = 'midfield'
                elif lsm_pos:
                        player_data['position'] = 'long stick midfield'
                #elif am_pos:
                        #player_data['position'] = 'attack/midfield'
                elif fo_pos:
                        player_data['position'] = 'face-off'

        #counter for the django "pk" field
        num += 1
        #create a player dictionary to transcribe to a JSON file for the eventual uploading to a Django Model.
        player_model = {"model": "player_data.Player",
                        "pk": num,
                        "fields": player_data.copy()}


        data.append(player_model.copy())


json.dump(data, total_output, sort_keys=True, indent=4)

f_read.close()
total_output.close()