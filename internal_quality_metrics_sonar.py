import json

# Carregar o JSON com as métricas do SonarQube
json_path = "analytics-raw-data/fga-eps-mds-2024.1-MeasureSoftGram-Action-02-12-2025-22-09-00-2024.1.json"
with open(json_path, "r") as file:
    sonar_data = json.load(file)
    
# Extração de todas as métricas, incluindo as do BaseComponent e componentes individuais

# Inicializar dicionário para armazenar métricas agregadas
aggregated_metrics = {
    "ncloc": 0,  # Linhas de código totais
    "bugs": 0,  # Total de bugs
    "open_issues": 0,  # Total de issues abertas
    "confirmed_issues": 0,  # Total de issues confirmadas
    "blocker_violations": 0,  # Violações bloqueadoras
    "critical_violations": 0,  # Violações críticas
    "files": 0  # Total de arquivos analisados
}

# Função para somar métricas do componente fornecido
def sum_metrics(component):
    for measure in component.get("measures", []):
        if measure["metric"] in aggregated_metrics:
            aggregated_metrics[measure["metric"]] += int(measure["value"])

# Somar métricas do BaseComponent
sum_metrics(sonar_data["baseComponent"])

# Somar métricas de cada componente individual
for component in sonar_data.get("components", []):
    sum_metrics(component)

# Cálculo do Bug Density LOC considerando todas as métricas
bug_density_loc = 1 - ((aggregated_metrics["bugs"] + aggregated_metrics["open_issues"] + aggregated_metrics["confirmed_issues"]) / aggregated_metrics["ncloc"] if aggregated_metrics["ncloc"] > 0 else 1)

# Cálculo do cumprimento das regras críticas/bloqueadoras
critical_blocker_issues = aggregated_metrics["blocker_violations"] + aggregated_metrics["critical_violations"]
fulfillment_critical_blocker_rules = 1 - (critical_blocker_issues / aggregated_metrics["files"] if aggregated_metrics["files"] > 0 else 1)

# Exibir os resultados com todas as métricas agregadas
aggregated_results = {
    "Total Lines of Code (ncloc)": aggregated_metrics["ncloc"],
    "Total Bugs": aggregated_metrics["bugs"],
    "Total Open Issues": aggregated_metrics["open_issues"],
    "Total Confirmed Issues": aggregated_metrics["confirmed_issues"],
    "Total Blocker Violations": aggregated_metrics["blocker_violations"],
    "Total Critical Violations": aggregated_metrics["critical_violations"],
    "Total Files": aggregated_metrics["files"],
    "Bug Density LOC": bug_density_loc,
    "Fulfillment of Critical/Blocker Quality Rules": fulfillment_critical_blocker_rules
}

print(aggregated_results)