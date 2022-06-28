import requests, json, re, os
from bs4 import BeautifulSoup

ERGAST_REQUEST = "https://ergast.com/api/f1/current/next.json"
SCHEDULE_F1_REQUEST = "https://www.formula1.com/en/racing/{year}.html"
BASE_F1_REQUEST = "https://www.formula1.com"

def extract_practice_times(url):
    """
    Extracts the times from the url (practice rounds)
    """
    result = []

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find_all("table", {"class": "resultsarchive-table"})[0]
    tbody = table.find_all("tbody")[0]
    trs = tbody.find_all("tr")

    for tr in trs:
        tds = tr.find_all("td")

        name = tds[3].text.strip()
        name = name[:name.rfind("\n")].replace("\n", " ")

        time = tds[5].text
        result.append((name, time if len(time) > 0 else "DNF"))

    return result

def extract_qualifying_times(url):
    """
    Extracts the times from the url (qualifying rounds)
    """
    result = []

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find_all("table", {"class": "resultsarchive-table"})[0]
    tbody = table.find_all("tbody")[0]
    trs = tbody.find_all("tr")

    for tr in trs:
        tds = tr.find_all("td")

        name = tds[3].text.strip()
        name = name[:name.rfind("\n")].replace("\n", " ")

        times = sorted([tds[x].text if len(tds[x].text) > 0 else "DNF" for x in range(5, 8)])
        result.append((name, times[0]))

    return result

def extract_race(url, year, race):
    """
    Extracts the results from the url (race)
    """
    results = {}

    response = requests.get(url)

    if "Sprint" in response.text: return None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    pages = ['js-practice-1', 'js-practice-2', 'js-practice-3', "js-qualifying"]
    for page in pages:
        try:
            div = soup.find_all("div", {"class": page})[0]
            results_button = div.find_all("a", {"class": "btn"})[0]

            if results_button.text.strip() != "results":
                times = []
            else:
                results_url = results_button.get("href")
                times = extract_practice_times(results_url)

            if "practice" in page:
                parse_results(results, page, times)
            else:
                parse_results(results, page, times)
        except:
            continue

    date = soup.find_all("p", {"class": "race-weekend-dates"})[0].text.strip()

    if "js-qualifying" in results:
        results["placements"] = [k for k in results["js-qualifying"]]

    results["track-name"] = f'{date} {year} ({re.findall(r"/([^//]+).html", url)[0]})'

    if not os.path.isdir(f"races/{year}"):
        os.mkdir(f"races/{year}")

    with open(f"races/{year}/{race}.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

def parse_results(d, round, results):
    if not results: return

    round_d = {}
    for result in results:
        round_d[result[0]] = result[1]
    d[round] = round_d

def get_url(year, round):
    url = SCHEDULE_F1_REQUEST.replace("{year}", str(year))

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    link = soup.find_all("a", {"data-roundtext": f"ROUND {round}"})[0]["href"]
    return BASE_F1_REQUEST + link

def automatically_extract_results():
    response = requests.get(ERGAST_REQUEST)
    data = json.loads(response.text)

    year = data["MRData"]["RaceTable"]["season"]
    round = data["MRData"]["RaceTable"]["round"]
    url = get_url(year, round)

    extract_race(url, year, round)

automatically_extract_results()