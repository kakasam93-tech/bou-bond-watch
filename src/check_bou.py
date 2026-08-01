import requests

url = "https://bou.or.ug/financial-markets/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers, timeout=30)

print("=" * 60)
print("Status Code:", response.status_code)
print("Final URL :", response.url)
print("Content Type:", response.headers.get("Content-Type"))
print("=" * 60)

print("\nFIRST 1000 CHARACTERS OF THE RESPONSE:\n")
print(response.text[:1000])