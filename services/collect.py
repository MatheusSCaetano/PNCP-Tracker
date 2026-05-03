import requests

def get_editais():
    url = "https://pncp.gov.br/api/pncp/v1/orgaos"
    
    headers = {
        "User-Agent" : "Mozilla/5.0",
        "Accept":"application/json"
    }
    
    try:
        response = requests.get(
            url, 
            headers=headers, 
            timeout=10,
        )
        if response.status_code == 200:
            return response.json()
    except:
        pass

    # print("URL usada:", url)
    # print("responseUrl: ", response.url)
    # print(response.status_code)
    # print(response.text[:500]) 

    return []