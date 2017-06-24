import bs4
import requests
import string
import re
import csv
import json


def main():
    team_count = 0
    fail_count = 0
    head_fail = []
    header_list = []
    header_fail = []
    header_pass = []
    recheck_header_child = []
    list_of_index_dict = []
    index_dict = {}
    num = 0


    #Text file containing University name, league, and roster URL
    f_read = open("ivy.txt", "rt")
    writing = open("ivy_writing_output", "a")
    player_out = open("ivy_player_output", "w")
    data = []
    #Dictionary variable containing individual player data, which is then transcribed to JSON
    #player_data = {"position": "", "year": "", "number": "", "height": "", "weight": "", "state": ""}
    player_model = {}
    data = []
    player_data = {}
    #Create single JSON output file
    total_output = open("ivy_player_data.json", "w")

    #CSV object of University text file
    reader = csv.reader(f_read)

    #Iterates through each University included in the original text file
    for indx_0, line in enumerate(reader):
        team_count += 1
        th_titles = []
        td_titles = []
        #HTTP request to roster URL
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0)'}
        page = requests.get(line[3].strip(), headers = headers)
        #Create Beautiful Soup object out of the fetched HTML
        page.raise_for_status()
        soup = bs4.BeautifulSoup(page.content, "html.parser")
        #Write a player's University and League to dictionary variable
        player_data['school'] = line[0].strip()
        player_data['league'] = line[1].strip()
        player_data['division'] = line[2].strip()

        #Find all HTML table rows in the Beautiful Soup object

        head_ths_fail = False
        head_tds_fail = False
        head = soup.find("thead")

        #Can we find table rows and table headers?
        try: 
            head_trs = head.find("tr")
            head_ths = head_trs.find_all("th")
        #Set this bool to true if error when looking for ths
        except:
            head_ths_fail = True
            fail_count += 1

        #Can we find table data cells?
        try:
            head_trs = head.find("tr")
            head_tds = head_trs.find_all("td")
        #Set this bool to true if error when looking for tds
        except:
            head_tds_fail = True
            fail_count += 1

        #If we found TDS, loop through each td and append to a list
        if head_tds_fail == False:
            for head_td in head_tds:
                td_titles.append(head_td.get_text().strip())

        #If we found THS, loop through each th and append to a list
        if head_ths_fail == False:
            for head_th in head_ths:
                th_titles.append(head_th.get_text().strip())
         

        #Check if we found any TDS, and that we found more than 2 tds (Valid data check)
        if td_titles != [] and len(td_titles) > 2:
            writing.write(str(player_data["school"]) + str(td_titles) + "\n")
            header_list = td_titles
        #Check if we have some data, but it isn't what we are looking for. 
        elif td_titles != [] and not len(td_titles) > 2:
            writing.write(str(player_data["school"]) + "Other THEAD Data")
            recheck_header_child.append(line)            
        #Check if we found any TDS, and that we found more than 2 tds (Valid data check)
        if th_titles != [] and len(th_titles) > 2:
            writing.write(str(player_data["school"]) + str(th_titles) + "\n")
            header_list = th_titles
        #Check if we have some data, but it isn't what we are looking for. 
        elif th_titles != [] and not len(th_titles) > 2:
            writing.write(str(player_data["school"]) + "Other THEAD Data\n")
            recheck_header_child.append(line)
        
        #If we found nothing, then save to different method
        if th_titles == [] and td_titles == []:
            writing.write(str(player_data["school"] + " FAIL\n"))
            header_fail.append(line)
        #elif len(th_titles) > 2 or len(td_titles) > 2:
            #header_data = {"player_data": player_data.copy(), "header_data": header_list}
            #header_pass.append(header_data.copy())

        
        for index, column in enumerate(header_list):
            player_number = re.search(r'No\.$|NO\.$|NO$|No$', column)
            player_name = re.search(r'NAME$|Name$', column)
            player_pos = re.search(r'Pos\.$|POS$|Position$|Pos$', column)
            player_ht = re.search(r'HT\.$|Ht\.$|Height$', column)
            player_wt = re.search(r'WT\.$|Wt\.$|Weight$', column)
            player_year = re.search(r'Cl\.$|CL\.$|Yr\.$|YR\.$|YEAR$|Year$|Class$|CLASS$', column)

            if player_number:
                player_number_index = index
            elif player_name:
                player_name_index = index
            elif player_pos:
                player_pos_index = index
            elif player_ht:
                player_ht_index = index
            elif player_wt:
                player_wt_index = index
            elif player_year:
                player_year_index = index
            

        #Find all HTML table rows in the Beautiful Soup object
        trs = soup.find_all("tr")

        #Iterate over each HTML table row
        
        for tr in trs:
            #Find all HTML table data cells
            tds = tr.find_all("td")
            #Iterate over each table data cell
            for index_0, td in enumerate(tds):
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

                td_data = td.get_text().replace("\n", "").replace("\t", "").strip()
                if index_0 == player_number_index:
                    player_data["number"] = str(td_data)
                elif index_0 == player_name_index:
                    player_data["name"] = str(td_data)
                elif index_0 == player_pos_index:
                    a_pos = re.search(r'a$|A$|Attack$|attack$', str(td_data))
                    d_pos = re.search(r'd$|D$|Defense$|defense$', str(td_data))
                    g_pos = re.search(r'g$|G$|GK$|Gk$|gk$|Goalie$', str(td_data))
                    m_pos = re.search(r'm$|M$|Middie$|middie$', str(td_data))
                    lsm_pos = re.search(r'LSM$|lsm$', str(td_data))
                    am_pos = re.search(r'A\/M$|a\/m$\M\/A$|m\/a$', str(td_data))
                    fo_pos = re.search(r'F\/O|Face-off$|Face-Off$|FO$|FO\/M$|M\/FO$', str(td_data))
                    if a_pos:
                        player_data["position"] = "Attack"
                    elif d_pos:
                        player_data["position"] = "Defense"
                    elif g_pos:
                        player_data["position"] = "Goalie"
                    elif m_pos:
                        player_data["position"] = "Midfield"
                    elif lsm_pos:
                        player_data["position"] = "Long Stick Midfield"
                    elif am_pos:
                        player_data["position"] = "Attack/Midfield"
                    elif fo_pos:
                        player_data["position"] = "FaceOff"
                    else:
                        player_data["position"] = ""
                elif index_0 == player_ht_index:
                    player_data['height'] = str(td_data)
                elif index_0 == player_wt_index:
                    player_data["weight"] = str(td_data)
                elif index_0 == player_year_index:
                    fr_year = re.search(r'fr\.$|Fr\.$|fr$|Fr$|^freshman$|^Freshman$', str(td_data))
                    so_year = re.search(r'so\.$|So\.$|so$|So$|^sophomore$|^Sophomore$', str(td_data))
                    jr_year = re.search(r'jr\.$|Jr\.$|jr$|Jr$|^junior$|^Junior$', str(td_data))
                    sr_year = re.search(r'sr\.$|Sr\.$|Sr$|Sr$|^Senior$|^Senior$', str(td_data))
                    if fr_year:
                        player_data["year"] = "Freshman"
                    elif so_year:
                        player_data["year"] = "Sophomore"
                    elif jr_year:
                        player_data["year"] = "Junior"
                    elif sr_year:
                        player_data["year"] = "Senior"

        
        if player_data["number"] and player_data["position"] and player_data["height"] and player_data["weight"] and player_data["year"]:
            num += 1
            player_model = {"model": "player_data.Player",
                            "pk": num,
                            "fields": player_data.copy()}
            data.append(player_model.copy())

        mismatch = re.search(r'^\d{1,2}$', player_data["name"])
        if mismatch:
            print(str(player_data["school"]) + ": MISMATCH")
            for tr in trs:
                #Find all HTML table data cells
                tds = tr.find_all("td")
                #Iterate over each table data cell
                for index_0, td in enumerate(tds):
                    if index_0 == player_number_index:
                        player_data["number"] = str(tds[index_0 + 1].get_text().replace("\n", "").replace("\t", "").strip())
                    elif index_0 == player_name_index:
                        player_data["name"] = str(tds[index_0 + 1].get_text().replace("\n", "").replace("\t", "").strip())
                    elif index_0 == player_pos_index:
                        a_pos = re.search(r'a$|A$|Attack$|attack$', str(tds[index_0 + 1].get_text().replace("\n", "").replace("\t", "").strip()))
                        d_pos = re.search(r'd$|D$|Defense$|defense$', str(tds[index_0 + 1].get_text().replace("\n", "").replace("\t", "").strip()))
                        g_pos = re.search(r'g$|G$|GK$|Gk$|gk$|Goalie$', str(tds[index_0 + 1].get_text().replace("\n", "").replace("\t", "").strip()))
                        m_pos = re.search(r'm$|M$|Middie$|middie$', str(tds[index_0 + 1].get_text().replace("\n", "").replace("\t", "").strip()))
                        lsm_pos = re.search(r'LSM$|lsm$', str(tds[index_0 + 1].get_text().replace("\n", "").replace("\t", "").strip()))
                        am_pos = re.search(r'A\/M$|a\/m$\M\/A$|m\/a$', str(tds[index_0 + 1].get_text().replace("\n", "").replace("\t", "").strip()))
                        fo_pos = re.search(r'F\/O|Face-off$|Face-Off$|FO$|FO\/M$|M\/FO$', str(tds[index_0 + 1].get_text().replace("\n", "").replace("\t", "").strip()))
                        if a_pos:
                            player_data["position"] = "Attack"
                        elif d_pos:
                            player_data["position"] = "Defense"
                        elif g_pos:
                            player_data["position"] = "Goalie"
                        elif lsm_pos:
                            player_data["position"] = "Long Stick Midfield"
                        elif m_pos:
                            player_data["position"] = "Midfield"
                        elif am_pos:
                            player_data["position"] = "Attack/Midfield"
                        elif fo_pos:
                            player_data["position"] = "FaceOff"
                        else:
                            player_data["position"] = ""
                    elif index_0 == player_ht_index:
                            player_data["height"] = str(tds[index_0 + 1].get_text().replace("\n", "").replace("\t", "").strip())
                    elif index_0 == player_wt_index:
                        player_data["weight"] = str(tds[index_0 + 1].get_text().replace("\n", "").replace("\t", "").strip())
                    elif index_0 == player_year_index:
                        fr_year = re.search(r'fr\.$|Fr\.$|fr$|Fr$|^freshman$|^Freshman$', str(tds[index_0 + 1].get_text().replace("\n", "").replace("\t", "").strip()))
                        so_year = re.search(r'so\.$|So\.$|so$|So$|^sophomore$|^Sophomore$', str(tds[index_0 + 1].get_text().replace("\n", "").replace("\t", "").strip()))
                        jr_year = re.search(r'jr\.$|Jr\.$|jr$|Jr$|^junior$|^Junior$', str(tds[index_0 + 1].get_text().replace("\n", "").replace("\t", "").strip()))
                        sr_year = re.search(r'sr\.$|Sr\.$|Sr$|Sr$|^Senior$|^Senior$', str(tds[index_0 + 1].get_text().replace("\n", "").replace("\t", "").strip()))
                        if fr_year:
                            player_data["year"] = "Freshman"
                        elif so_year:
                            player_data["year"] = "Sophomore"
                        elif jr_year:
                            player_data["year"] = "Junior"
                        elif sr_year:
                            player_data["year"] = "Senior"
                        else:
                            player_data["year"] = " "
                            
                num += 1
                player_model = {"model": "player_data.Player",
                                "pk": num,
                                "fields": player_data.copy()}
                data.append(player_model.copy())

    json.dump(data, total_output, sort_keys=True, indent=4)








if __name__ == "__main__":
    main()

"""
height_match = re.search(r'^(\d)-(\d{1,2})$', str(tds[index_0 + 1].get_text().replace("\n", "").replace("\t", "").strip()))
feet = int(height_match.group(1))
inches = int(height_match.group(2))
total_height = (feet * 12) + inches
player_data['height'] = int(total_height)
"""
