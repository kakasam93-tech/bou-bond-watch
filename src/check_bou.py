import requests

url = "https://bou.or.ug/financial-markets/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)

print("Status:", response.status_code)
print("Final URL:", response.url)
print("Content-Type:", response.headers.get("Content-Type"))

print("\nFirst 1000 characters:\n")
print(response.text[:1000])
