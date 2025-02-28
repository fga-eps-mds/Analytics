## Esses notebooks foram desenvolvidos para apoiar as atividades de análise de dados da qualidade de produto de software durante o ciclo de vida dos projetos das disciplinas.
### O modelo de qualidade utilizado como referência é o [Q-Rapids](https://github.com/fga-eps-mds/Analytics/blob/master/q-rapids%20model-doc.pdf).
### Tutorial de configuração do SonarCloud e GitHub: [tutorial](https://github.com/fga-eps-mds/Analytics/blob/master/tutorial-sonarcloud/Tutorial_SonarCloud_GitHub.md)


# Análise de Métricas com SonarQube

Este repositório contém scripts para obter e analisar métricas de qualidade de código utilizando o **SonarQube** e o **GitHub**.

## Arquivos

- **analytics_metric_sonar.ipynb**: Notebook Jupyter para visualização e análise de métricas extraídas do SonarQube.
- **create_metrics_sonar.py**: Script Python que interage com a API do GitHub e SonarQube para coletar informações sobre PRs mescladas e executar análises de qualidade de código. Esse deve rodar dentro do Repositório do Core|Front|Service

## Configuração e Uso

### 1. Instalação de Dependências
Certifique-se de ter as bibliotecas necessárias instaladas:
```sh
pip install requests python-dotenv
```

### 2. Configuração das Variáveis de Ambiente
Crie um arquivo **.env** na raiz do projeto e adicione suas credenciais:
```
GITHUB_TOKEN=seu_token_do_github
SONAR_TOKEN=seu_token_do_sonarqube
SONAR_HOST=http://localhost:9000  # Ou URL do seu servidor SonarQube
```

### 3. Execução do Script
Execute o script para coletar e analisar métricas do SonarQube:
```sh
python create_metrics_sonar.py
```

### 4. Uso do Notebook
Abra o notebook Jupyter para visualizar os dados coletados:
```sh
jupyter notebook analytics_metric_sonar.ipynb
```
