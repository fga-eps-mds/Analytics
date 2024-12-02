# Tutorial SonarCloud e Métricas do GitHub

Esse tutorial busca ajudar os estudantes das disciplinas EPS/MDS a configurar o SonarCloud com os repositórios para análise de qualidade e a criação dos arquivos no repositório de documentação. Além disso, no *parser_template.py* implementado, há também a coleta de métricas por parte do GitHub (*workflow runs*).

## Criando Projeto no SonarCloud

1. Entre com a sua conta no [SonarCloud](https://sonarcloud.io/projects);
2. Clique no "+" no canto superior direito e abra a página de "[Analyze new project](https://sonarcloud.io/projects/create)";
3. Escolha a organização "UnB/FGA-EPS-MDS", selecione os seus repositórios e clique em "Set Up";
4. Avance com as opções *default*.

Com isso, os projetos estarão disponíveis na tela inicial de "My Projects".

## Configurando Repositório com SonarCloud (enviar dados)

Essa parte deve ser feita em cada repositório de código-fonte.

### Arquivo sonar-project.properties

1. Na root do repositório, crie um arquivo chamada `sonar-project.properties`;
2. Ele deverá o conteúdo configurado de acordo com a linguagem de programação e o projeto com suas particularidades, exemplos de diferentes projetos:
    * [Python (FastAPI)](https://github.com/fga-eps-mds/2024.1-UnB-TV-Admin/blob/develop/sonar-project.properties);
    * [TypeScript (React)](https://github.com/fga-eps-mds/2023-2-CAPJu-Front/blob/develop/sonar-project.properties);
    * [Python (Django)](https://github.com/fga-eps-mds/2023-2-MeasureSoftGram-Service/blob/develop/sonar-project.properties).
    * [Dart (Flutter)](https://github.com/fga-eps-mds/2024.2-ARANDU-APP/blob/dev/sonar-projects.properties)

O importante é esse arquivo excluir a pasta de testes (e outras que não sejam do código fonte em si) dos dados coletados.

### Actions - Envia dados ao SonarCloud

1. Na root do repositório, crie a pasta *.github* e, dentro desta, a pasta *workflows*, onde serão cadatradas as actions;
2. Crie um arquivo que será responsável por enviar os dados de análise do código para o SonarCloud, exemplo de nome: *code-analysis.yml*. Detalhes sobre o conteúdo desse arquivo:
    * Configurar o ambiente do projeto para execução dos testes;
    * Gerar arquivo(s) com a cobertura (coverage) dos testes;
    * Executar o SonarCloud scan;
    * As variáveis de ambiente devem ser atribuídas como variáveis *secrets* de um *enviroment* no Github: [Como usar secrets no Github](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions).
      - [Criar SONAR_TOKEN](https://docs.sonarsource.com/sonarqube/latest/user-guide/user-account/generating-and-using-tokens/#generating-a-token).

Exemplos de arquivos para executar testes e SonarCloud:
- [Python (FastAPI)](https://github.com/fga-eps-mds/2024.1-UnB-TV-Admin/blob/develop/.github/workflows/code-analysis.yml);
- [Python (Django)](https://github.com/fga-eps-mds/2023-2-MeasureSoftGram-Service/blob/develop/.github/workflows/test.yml);
- [TypeScript (FrontEnd)](https://github.com/fga-eps-mds/2023.1-Dnit-Front/blob/main/.github/workflows/sonarcloud.yml).
- [Dart (Flutter)](https://github.com/fga-eps-mds/2024.2-ARANDU-APP/blob/dev/.github/workflows/code-analysis.yml)

Essa action é executada a cada push na branch principal do repositório.

## Criando Arquivos de Métricas no Repositório de Documentação

### Parser

1. Na root do projeto, criar a pasta *sonar_scripts* e nele o arquivo *parser_template.py*;
2. Copie o arquivo *parser_template.py*, presente na pasta root deste repositório, com o nome *parser.py*.

Esse arquivo é responsável por extrair os dados do SonarCloud e do Github e criar uma Release com a Tag baseado na label do Pull Request.

### Actions - Envia métricas do SonarCloud ao Repositório de Documentação

1. Na pasta *.github/workflows* na root do projeto, crie um arquivo para a action de enviar métricas, ele pode se chamar *release.yml*;
2. O seu conteúdo deve ser o seguinte:

```
name: Export de métricas

on: 
  pull_request:
    branches:
      - main
      - develop
    types: [ closed ]

jobs:
  release:
    if: github.event.pull_request.merged == true && contains(github.event.pull_request.labels.*.name, 'NOT RELEASE') == false
    runs-on: "ubuntu-latest"
    environment: actions
    
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
          
      - name: Install dotenv
        run: pip install python-dotenv packaging pandas
          
      - name: Cria arquivo .env
        run: |
          touch ./sonar_scripts/.env
          echo GITHUB_TOKEN=${{ secrets.API_TOKEN_GITHUB }} >> ./sonar_scripts/.env
          echo RELEASE_MAJOR=${{ contains(github.event.pull_request.labels.*.name, 'MAJOR RELEASE') }} >> ./sonar_scripts/.env
          echo RELEASE_MINOR=${{ contains(github.event.pull_request.labels.*.name, 'MINOR RELEASE') }} >> ./sonar_scripts/.env
          echo RELEASE_FIX=${{ contains(github.event.pull_request.labels.*.name, 'FIX RELEASE') }} >> ./sonar_scripts/.env
          echo DEVELOP=${{ contains(github.event.pull_request.labels.*.name, 'DEVELOP') }} >> ./sonar_scripts/.env
          echo REPO=${{ github.event.repository.name }} >> ./sonar_scripts/.env
          echo REPO_DOC=${{ secrets.REPO_DOC }} >> ./sonar_scripts/.env

      - name: Criar diretório
        run: mkdir -p analytics-raw-data

      - name: Coletar métricas no SonarCloud
        run: python ./sonar_scripts/parser.py

      - name: Envia métricas para repo de Doc
        run: |
          git config --global user.email "${{secrets.USER_EMAIL}}"
          git config --global user.name "${{secrets.USER_NAME}}"
          git clone --single-branch --branch main "https://x-access-token:${{ secrets.API_TOKEN_GITHUB }}@github.com/fga-eps-mds/${{ secrets.REPO_DOC }}" doc
          mkdir -p doc/analytics-raw-data
          cp -R analytics-raw-data/*.json doc/analytics-raw-data
          cd doc
          git add .
          git commit -m "Adicionando métricas do repositório ${{ github.event.repository.name }} ${{ github.ref_name }}"
          git push
```

3. De forma semelhante a outra action, algumas variáveis devem ser atribuídas como variáveis *secrets* de um *enviroment* no Github ([Como usar secrets no Github](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions)):
    * [API_TOKEN_GITHUB](API_TOKEN_GITHUB);
    * **USER_EMAIL** e **USER_NAME**: seu e-mail e nome no Github.
    * **REPO_DOC**: deve ser o nome do repositório de documentação, que possui as issues a serem analisadas.

Esse arquivo é executado a cada Pull Request fechado na branch principal do repositório.

### Labels Pull Request

Para o funcionamento ideal do **parser** ao criar as Releases, é necessário que os Pull Requests feitos tenham uma das seguintes labels (crie eles na aba de "Pull requests" do projeto):

A Tag da release segue o seguinte padrão: XX.YY.ZZ.

* **FIX RELEASE**: é responsável por incrementar **ZZ**;
* **MINOR RELEASE**: é responsável por incrementar **YY**;
* **MAJOR RELEASE**: é responsável por incrementar **XX**.

A label **NOT RELEASE** pode ser usada e não executa a action de criar o arquivo de métricas no repositório de documentação.
