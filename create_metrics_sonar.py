import requests
import os
import json
import subprocess
from dotenv import load_dotenv

# Carrega variáveis de ambiente (.env)
load_dotenv()

# Configurações do SonarQube
SONAR_TOKEN = os.getenv('SONAR_TOKEN')
PROJECT_KEY = "Service"
BASE_URL_SONAR = "http://localhost:9000"
SONAR_SCANNER_PATH = "/home/caiovitor/Documentos/sonar-scanner-6.2.1.4610-linux-x64/bin/sonar-scanner"

# Cabeçalhos para autenticação
headers = {"Authorization": f"Bearer {SONAR_TOKEN}"}

# Lista para armazenar métricas de cada branch
all_metrics = []

# 1️⃣ **Obter todas as branches do Git local**
print("Buscando branches locais do Git...")
try:
    git_branches = subprocess.check_output(["git", "branch","-a"], universal_newlines=True)
    branches = [b.strip().replace("* ", "") for b in git_branches.split("\n") if b.strip()]
except Exception as e:
    print(f"Erro ao obter branches do Git: {e}")
    exit(1)

# Iterar sobre cada branch
for branch_name in branches:
    branch_project_key = f"{PROJECT_KEY}-{branch_name.replace('/', '-')}"

    print(f"\nProcessando branch: {branch_name}")

    # 2️⃣ **Fazer checkout para a branch**
    print(f"Fazendo checkout para branch: {branch_name}")
    try:
        subprocess.run(["git", "checkout", branch_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao fazer checkout para {branch_name}: {e}")
        continue  # Pula para a próxima branch

    # 3️⃣ **Criar um novo projeto no SonarQube para a branch**
    print(f"Criando projeto no SonarQube: {branch_project_key}")
    data_project = {
        "project": branch_project_key,
        "name": branch_project_key,
        "visibility": "private"
    }
    response_project = requests.post(f"{BASE_URL_SONAR}/api/projects/create", headers=headers, data=data_project)

    if response_project.status_code == 200:
        print(f"Projeto '{branch_project_key}' criado com sucesso!")
    else:
        print(f"Projeto '{branch_project_key}' pode já existir. Continuando...")

    # 4️⃣ **Rodar o sonar-scanner para a branch**
    print(f"Rodando análise do SonarQube para {branch_name}...")
    sonar_command = [
        SONAR_SCANNER_PATH,
        f"-Dsonar.projectKey={branch_project_key}",
        "-Dsonar.sources=src",
        f"-Dsonar.host.url={BASE_URL_SONAR}",
        f"-Dsonar.login={SONAR_TOKEN}",
        "-Dsonar.verbose=true"
    ]

    try:
        subprocess.run(sonar_command, check=True)
        print(f"Análise concluída para {branch_name}")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao rodar o sonar-scanner para {branch_name}: {e}")
        continue

