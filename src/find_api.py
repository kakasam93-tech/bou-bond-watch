import requests

url = "https://bou.or.ug/financial-markets/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)

print("Status:", response.status_code)
print()

print("Server:", response.headers.get("Server"))
print()

print("Content-Type:", response.headers.get("Content-Type"))
print()

print("Interesting headers:")

for k, v in response.headers.items():
    if any(x in k.lower() for x in [
        "api",
        "server",
        "content",
        "cache",
        "cf",
        "x-",
        "vary"
    ]):
        print(f"{k}: {v}")