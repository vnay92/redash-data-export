import requests

url = "http://localhost:3000/sellerflex/api/health"

headers = {
    'Postman-Token': "3493fa94-700f-41a9-a16c-782ce0e98ca1,5f44e91b-7969-48cd-ae7d-659d6f51175e",
}

response = requests.request("GET", url, headers=headers)
darr = response.json()

l = '|time|status|'.split('|')

a = []
for d in darr:
    kv = [(k, d[k]) for k in l if k in d]
    a.append(kv)
    # print(kv)

print(a)
