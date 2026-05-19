
def filter(datas, password):
    result = []

    for item in datas:
        tittle = item.get("tittle") or ""
        description = item.get("description") or ""
       
        text = (tittle + " " + description).lower()

        if any(p.lower() in text for p in password):
            result.append(item)

    return result

