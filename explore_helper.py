# Helper function to emphasise words
def bold_string(string):
    return f"<b>{string}</b>"

# Explains the aggregation
def aggregate_explain(query_plan):
    strategy = query_plan["Strategy"]
    if strategy == "Sorted":
        result = "The rows are sorted based on their keys."
        if "Group Key" in query_plan:
            result += f" They are {bold_string('aggregated')} by the following keys: {', '.join(query_plan['Group Key'])}."
        if "Filter" in query_plan:
            result += f" They are filtered by {bold_string(query_plan['Filter'].replace('::text', ''))}."
        return result
    elif strategy == "Hashed":
        result = f"The rows are hashed based on the following key(s): {', '.join(query_plan['Group Key']).replace('::text', '')} which are then {bold_string('aggregated')} into bucket given by the hashed key."
        return result
    elif strategy == "Plain":
        return f"Result is simply {bold_string('aggregated')} as normal."
    return "Aggregation is not supported here."

# Explains the append
def append_explain(query_plan):
    return "This plan executes several sub-operations and combines all their results into a single set."

# Explains things that are missed out
def default_explain(query_plan):
    return f"The {query_plan['Node Type']} is performed."

# Explains the execution of certain function
def function_scan_explain(query_plan):
    return f"Executes {query_plan['Function Name']} and uses the output as the result set."
    
# Explains group by
def group_explain(query_plan):
    return f"Rows are grouped based on the following keys: {', '.join(query_plan['Group Key']).replace('::text', '')}."

# Explains hash
def hash_explain(query_plan):
    return "The hash function makes a memory hash with rows from the source."

# Explains the hash join
def hash_join_explain(query_plan):
    result = f"The result from previous operation is joined using hash {bold_string(query_plan['Join Type'])} {bold_string('Join')}"
    if "Hash Cond" in query_plan:
        result += f" on the condition: {bold_string(query_plan['Hash Cond'].replace('::text', ''))}"
    return result

# Explains the index scan
def index_scan_explain(query_plan):
    result = f"An {bold_string('index scan')} is done using the index table {bold_string(query_plan['Index Name'])}"
    if "Index Cond" in query_plan:
        result += f" with the following conditions: {bold_string(query_plan['Index Cond'].replace('::text', ''))}, and the {bold_string(query_plan['Relation Name'])} table and fetches rows pointed by indices matched in the scan."
    if "Filter" in query_plan:
        result += f" The result is then filtered by {bold_string(query_plan['Filter'].replace('::text', ''))}."
    return result

# Explains the index only scan
def index_only_scan_explain(query_plan):
    result = f"An index scan is done using the index table {bold_string(query_plan['Index Name'])}"
    if "Index Cond" in query_plan:
        result += f" with the condition(s) {bold_string(query_plan['Index Cond'].replace('::text', ''))}. It then returns the matches found in index table scan as the result."
    if "Filter" in query_plan:
        result += f" The result is then filtered by {bold_string(query_plan['Filter'].replace('::text', ''))}."
    return result

# Explains limit
def limit_explain(query_plan):
    return f"Instead of scanning the entire table, the scan is done with a {bold_string('limit')} of {query_plan['Plan Rows']} entries."

# Explains materialize
def materialize_explain(query_plan):
    return "The results of sub-operations are stored in memory for faster access."

# Explains merge join
def merge_join_explain(query_plan):
    result = f"The results from sub-operations are joined using {bold_string('Merge Join')}"
    if "Merge Cond" in query_plan:
        result += f" with the condition {bold_string(query_plan['Merge Cond'].replace('::text', ''))}"
    if "Join Type" == "Semi":
        result += " but only the row from the left relation is returned"
    return result

# Explains nested loop
def nested_loop_explain(query_plan):
    return f"The join results between the {bold_string('nested loop')} scans of the suboperations are returned as new rows."

# Explains sequential scan
def seq_scan_explain(query_plan):
    result = f"It does a {bold_string('sequential scan')} on relation "
    if "Relation Name" in query_plan:
        result += bold_string(query_plan["Relation Name"])
    if "Alias" in query_plan:
        if query_plan["Relation Name"] != query_plan["Alias"]:
            result += f" with an alias of {bold_string(query_plan['Alias'])}"
    if "Filter" in query_plan:
        result += f" and filtered with the condition {bold_string(query_plan['Filter'])}"
    result += "."
    return result

# Explains sort
def sort_explain(query_plan):
    result = f"The result is {bold_string('sorted')} using the attribute "
    if "DESC" in query_plan["Sort Key"]:
        result += f"{bold_string(str(query_plan['Sort Key']).replace('DESC', ''))} in descending order"
    elif "INC" in query_plan["Sort Key"]:
        result += f"{bold_string(str(query_plan['Sort Key']).replace('INC', ''))} in ascending order"
    else:
        result += bold_string(str(query_plan["Sort Key"]).replace("[", "\[").replace("]", "\]"))
    return result

# Explains subquery scan
def subquery_scan_explain(query_plan):
    return f"Performs a {bold_string('Subquery scan')} without futher processing or altering of results."

# Explains duplicate removal
def unique_explain(query_plan):
    return f"Filters out duplicate rows, and {bold_string('unique')} values are preserved."

# Explains values scan
def values_scan_explain(query_plan):
    return f"Does a {bold_string('values scan')} using given values from the query."

# Explorer class to store a hashmap of node types to explain functions
class Explorer(object):
    explorer_map = {
        "Aggregate": aggregate_explain,
        "Append": append_explain,
        "Function Scan": function_scan_explain,
        "Group": group_explain,
        "Index Scan": index_scan_explain,
        "Index Only Scan": index_only_scan_explain,
        "Limit": limit_explain,
        "Materialize": materialize_explain,
        "Unique": unique_explain,
        "Merge Join": merge_join_explain,
        "Subquery Scan": subquery_scan_explain,
        "Values Scan": values_scan_explain,
        "Seq Scan": seq_scan_explain,
        "Nested Loop": nested_loop_explain,
        "Sort": sort_explain,
        "Hash": hash_explain,
        "Hash Join": hash_join_explain,
    }
