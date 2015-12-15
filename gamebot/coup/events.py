
def completion(query_str, possible):
    if query_str in possible:
        return [query_str]
    else:
        found = []
        for try_str in possible:
            if try_str.startswith(query_str):
                found.append(try_str)
    return found
