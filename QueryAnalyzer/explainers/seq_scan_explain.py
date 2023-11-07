from QueryAnalyzer.explainers.color import bold_string


def seq_scan_explain(query_plan):
    sentence = f"It does a {bold_string('sequential scan')} on relation "
    if "Relation Name" in query_plan:
        sentence += bold_string(query_plan["Relation Name"])
    if "Alias" in query_plan:
        if query_plan["Relation Name"] != query_plan["Alias"]:
            sentence += f" with an alias of {bold_string(query_plan['Alias'])}"
    if "Filter" in query_plan:
        sentence += f" and filtered with the condition {bold_string(query_plan['Filter'])}"
    sentence += "."

    return sentence
