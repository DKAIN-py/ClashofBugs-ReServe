import requests

def send_to_express(data):
    try:
        response = requests.post(
            "http://localhost:8080/receiver/filter",
            json=data,
            headers={"Content-Type":"application/json"},
            timeout=20
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error sending data:{e}")
        raise