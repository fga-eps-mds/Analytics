import requests
import subprocess
import os
from dotenv import load_dotenv
from datetime import datetime

# Carregar variáveis do ambiente
load_dotenv()

# Configuração do GitHub
OWNER = "fga-eps-mds"
REPO = "2024.1-MeasureSoftGram-Core" # Mudar para Core, Front ou Service
GITHUB_TOKEN =os.getenv("GITHUB_TOKEN", "" )
HEADERS_GITHUB = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

# Configuração do SonarQube
SONAR_TOKEN = os.getenv("SONAR_TOKEN", "" )
if not SONAR_TOKEN:
    raise ValueError("SONAR_TOKEN não está definido. Verifique seu arquivo .env.")

BASE_URL_SONAR = os.getenv("SONAR_HOST", "http://localhost:9000")
SONAR_SCANNER_PATH = "/home/caiovitor/Documentos/sonar-scanner-6.2.1.4610-linux-x64/bin/sonar-scanner"
VERSAO = "1.5.8"  # Defina a versão do projeto

##################
# FUNÇÕES GITHUB #
##################

def get_closed_prs(owner, repo):
    """ Obtém os PRs fechados que foram mesclados e suas datas """
    prs = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=closed&per_page=100&page={page}"
        response = requests.get(url, headers=HEADERS_GITHUB)
        if response.status_code == 200:
            data = response.json()
            if not data:
                break
            for pr in data:
                if pr.get("merged_at"):
                    merge_commit_sha = pr.get("merge_commit_sha")
                    if merge_commit_sha:
                        prs.append((pr["number"], merge_commit_sha))
            page += 1
        else:
            print(f"Erro ao buscar PRs: {response.status_code}, {response.text}")
            break
    return prs

def get_commit_date(commit_sha):
    """ Obtém a data do commit de merge """
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/commits/{commit_sha}"
    response = requests.get(url, headers=HEADERS_GITHUB)
    if response.status_code == 200:
        commit_data = response.json()
        commit_date = commit_data["commit"]["committer"]["date"]
        return datetime.strptime(commit_date, "%Y-%m-%dT%H:%M:%SZ").strftime("%m-%d-%Y-%H-%M-%S")
    else:
        print(f"Erro ao obter data do commit {commit_sha}: {response.status_code}, {response.text}")
        return None

def run_sonar_analysis():
    print("🔍 Buscando pull requests mescladas através de commits de merge...")
    prs = get_closed_prs(OWNER, REPO)
    
    if not prs:
        print("⚠️ Nenhuma pull request mesclada encontrada.")
        return

    for pr_number, merge_commit in prs:
        if not merge_commit:
            print(f"⚠️ PR #{pr_number} não tem commit de merge. Pulando...")
            continue

        commit_timestamp = get_commit_date(merge_commit)
        if not commit_timestamp:
            print(f"⚠️ Não foi possível obter a data do commit {merge_commit}. Pulando...")
            continue

        branch_project_key = f"{OWNER}-{REPO}-{commit_timestamp}-{VERSAO}"
        print(f"\n🚀 Processando PR #{pr_number} - Último commit de merge: {merge_commit}")

        print(f"🔄 Fazendo checkout para commit: {merge_commit}")
        try:
            subprocess.run(["git", "fetch", "--all"], check=True)
            result = subprocess.run(["git", "checkout", merge_commit], check=True, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"⚠️ O commit {merge_commit} não existe localmente. Pulando...")
                continue
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao fazer checkout para {merge_commit}: {e}")
            continue

        print(f"🔹 Criando projeto no SonarQube: {branch_project_key}")
        check_project_url = f"{BASE_URL_SONAR}/api/projects/search?projects={branch_project_key}"
        response_check = requests.get(check_project_url, headers={"Authorization": f"Bearer {SONAR_TOKEN}"})

        if response_check.status_code == 200 and response_check.json().get("components"):
            print(f"⚠️ O projeto {branch_project_key} já existe no SonarQube. Pulando criação...")
        else:
            data_project = {"project": branch_project_key, "name": branch_project_key, "visibility": "private"}
            response_project = requests.post(
                f"{BASE_URL_SONAR}/api/projects/create",
                headers={"Authorization": f"Bearer {SONAR_TOKEN}"},
                data=data_project
            )
            if response_project.status_code not in [200, 201]:
                print(f"❌ Erro ao criar projeto no SonarQube: {response_project.text}")
                continue

        print(f"📡 Rodando análise do SonarQube para {merge_commit}...")
        sonar_command = [
            SONAR_SCANNER_PATH,
            f"-Dsonar.projectKey={branch_project_key}",
            "-Dsonar.sources=src",
            f"-Dsonar.host.url={BASE_URL_SONAR}",
            f"-Dsonar.token={SONAR_TOKEN}",
            "-Dsonar.verbose=true"
        ]
        try:
            subprocess.run(sonar_command, check=True)
            print(f"✅ Análise concluída para {merge_commit}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao rodar o sonar-scanner para {merge_commit}: {e}")
            continue

if __name__ == "__main__":
    run_sonar_analysis()
