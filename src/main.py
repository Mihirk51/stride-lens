from src.core.clients.base_api_client import BaseAPIClient


def main():
    client = BaseAPIClient("https://api.agify.io")

    response = client.get("", params={"name": "michael", "country_id": "US"})
    print(response.data)


if __name__ == "__main__":
    main()
