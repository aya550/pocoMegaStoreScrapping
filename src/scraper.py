import requests

BASE_URL = "https://ecommerce-playground.lambdatest.io/"
HEADERS = {"User-Agent": "IPSII-scraping-lab/1.0"}


def main():
    response = requests.get(BASE_URL, headers=HEADERS, timeout=10)
    print(response.status_code, len(response.text))


if __name__ == "__main__":
    main()
