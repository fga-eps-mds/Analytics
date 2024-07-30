import json
import requests
import sys
from datetime import datetime
import requests
# import datetime
import pandas as pd

TODAY = datetime.now()

METRICS_SONAR = [
    "files",
    "functions",
    "complexity",
    "comment_lines_density",
    "duplicated_lines_density",
    "coverage",
    "ncloc",
    "tests",
    "test_errors",
    "test_failures",
    "test_execution_time",
    "security_rating",
]

BASE_URL = "https://sonarcloud.io/api/measures/component_tree?component=fga-eps-mds_"

if __name__ == "__main__":

    REPO = sys.argv[1]
    RELEASE_VERSION = sys.argv[2]

    response = requests.get(
        f'{BASE_URL}{REPO}&metricKeys={",".join(METRICS_SONAR)}&ps=500'
    )
    j = json.loads(response.text)

    file_path = f'./analytics-raw-data/fga-eps-mds-{REPO}-{TODAY.strftime("%m-%d-%Y-%H-%M-%S")}-{RELEASE_VERSION}.json'

    with open(file_path, "w") as fp:
        fp.write(json.dumps(j))
        fp.close()
        
# _______________________________________________________________________________________________________________________________

    nome_arquivo_json = f'./analytics-raw-data/GitHub_API-fga-eps-mds-{REPO}-{TODAY.strftime("%m-%d-%Y-%H-%M-%S")}-{RELEASE_VERSION}.json'

    owner = "fga-eps-mds"
    repo = "2022-2-MeasureSoftGram-Core"
    # date = datetime.datetime.now().strftime("%Y-%m-%d")
    date = datetime.strptime("2023-03-23","%Y-%m-%d").strftime("%Y-%m-%d")

    # 2023-03-23T01:56:10Z

    # Utilize a api que for necessária
    # api_url_workflows = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows"
    # api_url_jobs = f"https://api.github.com/repos/{owner}/{repo}/actions/runs/3624383254/jobs"
    # api_url_deployments = f"https://api.github.com/repos/{owner}/{repo}/deployments"
    api_url_runs = f"https://api.github.com/repos/{owner}/{repo}/actions/runs"


    def all_request_pages(data):
        total_runs = data["total_count"]
        pages = (total_runs // 100) + (1 if total_runs % 100 > 0 else 0)
        for i in range(pages+1):
            if i == 0 or i == 1:
                continue
            api_url_now = api_url_runs + "?page=" + str(i)
            response = requests.get(api_url_now)
            for j in ((response.json()['workflow_runs'])):
                data['workflow_runs'].append(j)
        return data


    def filter_request_per_date(data, date):
        data_filtered = []
        for i in data["workflow_runs"]:
            if datetime.strptime(i["created_at"][:10],"%Y-%m-%d").strftime("%Y-%m-%d") == date:
                data_filtered.append(i)
        return {"workflow_runs": data_filtered}

    # Envia get request
    response = requests.get(api_url_runs,params={'per_page': 100,})

    # get the data in json or equivalent dict form at
    data = response.json()

    data =  filter_request_per_date(all_request_pages(data),date)

    print("Quantidade de workflow_runs: " + str(len(data["workflow_runs"])))

    # Salva os dados em um json file
    with open(nome_arquivo_json, "w") as arquivo_json:
        json.dump(data, arquivo_json)
    
    # _______________________________________________________________________________________________________________
