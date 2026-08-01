import requests

URL = "https://bou.or.ug/financial-markets/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(URL, headers=headers, timeout=30)

print("Status Code:", response.status_code)
print("Final URL:", response.url)
print("Content-Type:", response.headers.get("Content-Type"))
print("First 1000 characters:\n")
print(response.text[:1000])
