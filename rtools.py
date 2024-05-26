import time
import requests
import sys

from string import Template

# Extremely Hacky EOR Page & Table Scroller
# By Fry 2024
#
# To use: run python3 rtools.py <tournament_id>
# This produces index.html (EOR page for judges)
# and scroller.html (for projector)
# 
# Any questions, email, facebook or discord me.


# Configuration
api_base_url = 'https://melee.gg/api/match/list/current'
client_id = ''
client_secret = ''
headers = {'Accept': 'application/json', 'user-agent': None}

webpage_template = ""
scroller_template = ""

# Function to get the remaining active matches without a result
def get_active_matches(tournament_id):
    url = f'{api_base_url}/{tournament_id}?variables.pageSize=250&variables.ignoreCache=true'
    response = requests.get(url, auth=(client_id, client_secret), headers=headers, timeout=5)
    
    if response.status_code != 200:
        raise Exception(f"Error fetching data from API: {url} : {response.status_code} - {response.text} // {response.headers}")
    
    matches = response.json()
    
    active_matches = [
        {
            #'Player 1 Name': match['Competitors'][0]['Team']['Players'][0]['DisplayName'],
            #'Player 2 Name': match['Competitors'][1]['Team']['Players'][0]['DisplayName'],
            'table_no': match['TableNumber'],
            'time_ext': match.get('TimeExtensionMinutes') or 0,
            'staff': match.get('EndOfRoundStaffName') or ''
        }
        for match in matches["Content"] if not match['HasResult']
    ]
    active_matches.sort(key=lambda x: (-x['time_ext'], x['table_no']))
    return active_matches

def write_matches(active_matches):
    matches_processed = []
    for match in active_matches:
        if match['time_ext'] > 0:
            colour = "style='background-color: #eb6868;'"
        else:
            colour = ''
        matches_processed.append(f"<tr><td>{match['table_no']}</td><td {colour}>{match['time_ext']}</td><td>{match['staff']}</td></tr>")
    matches_sub = {'tables': '\n'.join(matches_processed)}
    with open('index.html', 'w') as f:
        result = webpage_template.substitute(matches_sub)
        f.write(result)
    scroller_sub = {'scroller_tables': '        '.join(f'{x["table_no"]}' for x in active_matches)}
    with open('scroller.html', 'w') as f:
        result = scroller_template.substitute(scroller_sub)
        f.write(result)
    return

if __name__ == "__main__":
    f = open('template.html', 'r')
    webpage_template = Template(f.read())
    f.close()
    if webpage_template == "":
        print("Couldn't read website template")
        sys.exit(0)
    f = open('scroller_template.html', 'r')
    scroller_template = Template(f.read())
    f.close()
    while True:
        try:
            active_matches = get_active_matches(sys.argv[1])
            print(f"Found {len(active_matches)} active matches")
            write_matches(active_matches)
        except Exception as e:
            print(f"An error occurred: {e}")
        time.sleep(30)