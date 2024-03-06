import requests

class SafeTech():

    def update(self) -> None:
        # Specify the URL of the API you want to connect with
        url = 'http://192.168.0.79:5333/safe-tec/get/ALL'

        # Send a GET request to the API
        response = requests.get(url)

        # Print the status code and the response body
        print('Status Code:', response.status_code)
        print('Response Body:', response.json())

        self.SRN = response.json()['SRN']

