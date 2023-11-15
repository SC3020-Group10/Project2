def bold_string(string):
    return f"<b>{string}</b>"

def aggregate_explain(query_plan):
    # For plans of the aggregate type: SortAggregate, HashAggregate, PlainAggregate
    strategy = query_plan["Strategy"]
    if strategy == "Sorted":
        result = "The rows are sorted based on their keys."
        if "Group Key" in query_plan:
            result += f" They are {bold_string('aggregated')} by the following keys: "
            for key in query_plan["Group Key"]:
                result += bold_string(key) + ","
            result = result[:-1]
            result += "."
        if "Filter" in query_plan:
            result += " They are filtered by " + bold_string(
                query_plan["Filter"].replace("::text", "")
            )
            result += "."
        return result
    elif strategy == "Hashed":
        result = "It hashes all rows based on the following key(s): "
        for key in query_plan["Group Key"]:
            result += bold_string(key.replace("::text", "")) + ", "
        result += f"which are then {bold_string('aggregated')} into bucket given by the hashed key."
        return result
    elif strategy == "Plain":
        return f"Result is simply {bold_string('aggregated')} as normal."
    else:
        raise ValueError(
            "Aggregate_explain does not work for strategy: " + strategy
        )
        
def append_explain(query_plan):
    result = "This plan simply runs multiple sub-operations, and returns all the rows that were returned as one resultset."
    return result

def cte_explain(query_plan):
    result = (
        f"A {bold_string('CTE scan')} is performed on the table "
        + bold_string(str(query_plan["CTE Name"]))
        + " which is stored in memory "
    )
    if "Index Cond" in query_plan:
        result += " with condition(s) " + bold_string(
            query_plan["Index Cond"].replace("::text", "")
        )
    if "Filter" in query_plan:
        result += " and then filtered by " + bold_string(
            query_plan["Filter"].replace("::text", "")
        )
    result += "."
    return result

def default_explain(query_plan):
    return "The {} is performed.".format(bold_string(query_plan["Node Type"]))

def function_scan_explain(query_plan):
    return "The function {} is run and returns the recordset created by it.".format(
        bold_string(query_plan["Function Name"])
    )
    
def group_explain(query_plan):
    result = f"The result from the previous operation is {bold_string('grouped')} together using the following keys: "
    for i, key in enumerate(query_plan["Group Key"]):
        result += bold_string(key.replace("::text", ""))
        if i == len(query_plan["Group Key"]) - 1:
            result += "."
        else:
            result += ", "
    return result

def hash_explain(query_plan):
    result = f"The {bold_string('hash')} function makes a memory {bold_string('hash')} with rows from the source."
    return result

def hash_join_explain(query_plan):
    result = ""
    result += f"The result from previous operation is joined using {bold_string('Hash')} {bold_string(query_plan['Join Type'])} {bold_string('Join')}"
    if "Hash Cond" in query_plan:
        result += " on the condition: {}".format(
            bold_string(query_plan["Hash Cond"].replace("::text", ""))
        )
    result += "."
    return result

def index_scan_explain(query_plan):
    result = ""
    result += (
        f"An {bold_string('index scan')} is done using an index table "
        + bold_string(query_plan["Index Name"])
    )
    if "Index Cond" in query_plan:
        result += " with the following conditions: " + bold_string(
            query_plan["Index Cond"].replace("::text", "")
        )
    result += ", and the {} table and fetches rows pointed by indices matched in the scan.".format(
        bold_string(query_plan["Relation Name"])
    )

    if "Filter" in query_plan:
        result += (
            " The result is then filtered by "
            + bold_string(query_plan["Filter"].replace("::text", ""))
            + "."
        )
    return result

def index_only_scan_explain(query_plan):
    result = ""
    result += "An index scan is done using an index table " + bold_string(
        query_plan["Index Name"]
    )
    if "Index Cond" in query_plan:
        result += " with condition(s) " + bold_string(
            query_plan["Index Cond"].replace("::text", "")
        )
    result += ". It then returns the matches found in index table scan as the result."
    if "Filter" in query_plan:
        result += (
            " The result is then filtered by "
            + bold_string(query_plan["Filter"].replace("::text", ""))
            + "."
        )

    return result

def limit_explain(query_plan):
    # https://www.depesz.com/2013/05/09/explaining-the-unexplainable-part-3/
    result = f"Instead of scanning the entire table, the scan is done with a {bold_string('limit')} of {query_plan['Plan Rows']} entries."
    return result

def materialize_explain(query_plan):
    # https://www.depesz.com/2013/05/09/explaining-the-unexplainable-part-3/
    result = "The results of sub-operations are stored in memory for faster access."
    return result

def merge_join_explain(query_plan):
    result = f"The results from sub-operations are joined using {bold_string('Merge Join')}"

    if "Merge Cond" in query_plan:
        result += " with condition " + bold_string(
            query_plan["Merge Cond"].replace("::text", "")
        )

    if "Join Type" == "Semi":
        result += " but only the row from the left relation is returned"

    result += "."
    return result

def nested_loop_explain(query_plan):
    result = f"The join results between the {bold_string('nested loop')} scans of the suboperations are returned as new rows."
    return result

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

def setop_explain(query_plan):
    # https://www.depesz.com/2013/05/19/explaining-the-unexplainable-part-4/
    result = "It finds the "
    cmd_name = bold_string(str(query_plan["Command"]))
    if cmd_name == "Except" or cmd_name == "Except All":
        result += "differences "
    else:
        result += "similarities "
    result += "between the two previously scanned tables using the {} operation.".format(
        bold_string(query_plan["Node Type"])
    )

    return result

def sort_explain(query_plan):
    result = f"The result is {bold_string('sorted')} using the attribute "
    if "DESC" in query_plan["Sort Key"]:
        result += (
            bold_string(str(query_plan["Sort Key"]).replace("DESC", ""))
            + " in descending order"
        )
    elif "INC" in query_plan["Sort Key"]:
        result += (
            bold_string(str(query_plan["Sort Key"]).replace("INC", ""))
            + " in increasing order"
        )
    else:
        result += bold_string(str(query_plan["Sort Key"]).replace("[", "\[").replace("]", "\]"))
    result += "."
    return result

def subquery_scan_explain(query_plan):
    result = f"{bold_string('Subquery scan')} is done on results from sub-operations but there are no changes."
    return result

def unique_explain(query_plan):
    result = f"Using the sorted data from the sub-operations, a scan is done on each row and only {bold_string('unique')} values are preserved."
    return result

def values_scan_explain(query_plan):
    result = f"A {bold_string('values scan')} is done using the given values from the query."
    return result

class Explorer(object):
    # Static Explorer class to store a hashmap of node types to explain functions
    explorer_map = {
        "Aggregate": aggregate_explain,
        "Append": append_explain,
        "CTE Scan": cte_explain,
        "Function Scan": function_scan_explain,
        "Group": group_explain,
        "Index Scan": index_scan_explain,
        "Index Only Scan": index_only_scan_explain,
        "Limit": limit_explain,
        "Materialize": materialize_explain,
        "Unique": unique_explain,
        "Merge Join": merge_join_explain,
        "SetOp": setop_explain,
        "Subquery Scan": subquery_scan_explain,
        "Values Scan": values_scan_explain,
        "Seq Scan": seq_scan_explain,
        "Nested Loop": nested_loop_explain,
        "Sort": sort_explain,
        "Hash": hash_explain,
        "Hash Join": hash_join_explain,
    }
