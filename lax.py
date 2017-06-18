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

    #Text file containing University name, league, and roster URL
    f_read = open("sites.txt", "rt")
    writing = open("writing_output", "w")
    player_out = open("player_output", "w")
    data = []
    #Dictionary variable containing individual player data, which is then transcribed to JSON
    player_data = dict()

    #Create single JSON output file
    total_output = open("final_player_data.json", "w")

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
            player_out.write(player_data["school"] + "\n")
            #Find all HTML table data cells
            tds = tr.find_all("td")
            #Iterate over each table data cell
            for index_0, td in enumerate(tds):
                td_data = td.get_text().replace("\n", "").replace("\t", "").strip()
                if index_0 == player_number_index:
                    player_out.write("Number: " + str(td_data) + "\n")
                elif index_0 == player_name_index:
                    player_out.write("Name: " + str(td_data) + "\n")
                elif index_0 == player_pos_index:
                    player_out.write("Position: " + str(td_data) + "\n")
                elif index_0 == player_ht_index:
                    player_out.write("Height: " + str(td_data) + "\n")
                elif index_0 == player_wt_index:
                    player_out.write("Weight: " + str(td_data) + "\n")
                elif index_0 == player_year_index:
                    player_out.write("Year: " + str(td_data) + "\n")
            player_out.write("\n")

if __name__ == "__main__":
    main()