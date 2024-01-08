# Hammurabi Python API Wrapper

This repository hosts an API wrapper for a comprehensive database of transaction data for the SOL-USDC pool on Orca, one of the leading decentralized exchanges on the Solana blockchain. The dataset includes detailed information on each transaction, providing valuable insights for traders, analysts, and enthusiasts.

The eventual aim is to expand the database to feature comprehensive coverage of Orca liquidity pool data and eventually provide coverage of additional decentralized exchanges on Solana such as Raydium. However the database is still a work in progress. The API wrapper serves as an easy way for end users to access this database, making DeFi data on Solana more accessible. 

## Routes 
**Raw Transactions**

- Endpoint: `/raw_transactions`
- Method: GET
- Headers: 
    - **API-Key:** The API key for authorization
- Response:
    - **200 OK:** Successfully retrieved price data
    - **401 Unauthorized:** Incorrect or missing API key
    - **403 Forbidden:** Monthly credit limit exceeded or rate limit exceeded.
  
**Prices**

- Endpoint: `/prices`
- Method: GET
- Headers: 
    - **API-Key:** The API key for authorization
- Response:
    - **200 OK:** Successfully retrieved price data
    - **401 Unauthorized:** Incorrect or missing API key
    - **403 Forbidden:** Monthly credit limit exceeded or rate limit exceeded.

**Metadata**

- Endpoint: `/metadata`
- Method: GET
- Headers: 
    - **API-Key:** The API key for authorization
- Response:
    - **200 OK:** Successfully retrieved metadata
    - **401 Unauthorized:** Incorrect or missing API key
    - **403 Forbidden:** Monthly credit limit exceeded or rate limit exceeded.

**Generate API Key**

- Endpoint: `/generate_api_key`
- Method: POST 
- Headers: 
    - **Authorization:** Basic Auth (username and password)
- Parameters:
    - **tier:** The tier of the API key (optional, defaults to 'free'). Can be 'free', 'builder', or 'pro'.
- Response:
    - **200 OK:** Successfully generates the API key
      ```
      {
        "new_api_key": "4uTLDK0H5CyxbsHtPTUNgA",
        "tier": "free"
      }
      ```
    - **401 Unauthorized:** Incorrect or missing authentication credentials

**Change API Key Tier**

- Endpoint: `/change_tier`
- Method: POST
- Headers:
    - **Authorization:** Basic Auth (username and password)
    - **Content-Type:** application/json
- Body (json):
    - **api_key:** The API key to change the tier of
    - **new_tier:** The new tier to assign to the API key

		```
	  {
	    		"api_key": "4uTLDK0H5CyxbsHtPTUNgA",
	    		"new_tier": "pro"
		}
- Response:
    - **200 OK:** Successfully changed the tier of the API key
      ```{ "message": "API key tier changed to pro" }```
    - **400 Bad Request:** Invalid tier specified
    - **401 Unauthorized:** Incorrect or missing authentication credentials
    - **404 Not Found:** API key not found

**Whitelist API Key**
- Endpoint: `/toggle_whitelist`
- Method: POST 
- Authentication: Basic Auth (username and password)
- Headers: 
    - **Authorization:** Basic Auth (username and password)
    - **Content-Type:** application/json
- Request Body (json)
    - **api_key:** The API key for which the whitelist status needs to be toggled
- Response: 
    - **200 OK:** Successfully toggled the whitelist status of the API key
    ```
    {
        "message": "API key 'mx_fkEO3Rt4L16ZlSdYkJg' whitelisting toggled",
        "whitelisted": true
    }
    ```
    - **401 Unauthorized:** Authentication failed due to incorrect or missing credentials 
    - **400 Bad Request:** The request is missing the required api_key parameter
    - **404 Not Found:** The specified API key was not found

  **Send Payment**
  - Endpoint: `/send_payment`
  - Method: POST 
  - Headers:
  	- **Content-Type:** application/json 
  - Request Body (json)
  	- **api_key:** The API key for which the payment is being made
   	- **token_amount:** The amount of Solana to send 	 
  - Response:
  	- **200 OK:** Successfully made a monthly payment and upgraded tier
   	- **400 Bad Request:** Payment amount is incorrect 	   

## Credit System 

**Free**
- 500k call credits per month
- 200 calls / min

**Builder**
- 2m call credits per month
- 200 calls / min

**Pro**
- 5m call credits per month
- 500 calls / min

## Integrating Into Code

The code below demonstrates how to call the API in Python. It is important to note that you must either be running the API locally and have access to your own database or reach out to me for a key. As this is an early stage API, there is no web interface in which a user can generate their own key yet. 

```
import requests

def get_api_data(endpoint, api_key=None):
    url = f"http://localhost:5000/{endpoint}"  # Change to the hosted API URL if not running locally
    headers = {"API-Key": api_key} if api_key else {}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error making request: {e}")
        return None

# Example usage
endpoint = 'raw_transactions'  # Can be 'raw_transactions', 'prices', etc.
api_key = 'your_api_key_here'  # Only needed for hosted API, omit for local API
data = get_api_data(endpoint, api_key)
print(data)
```

## Running On Local Machine 

Accessing the data on your local machine involves several steps. Whether you prefer postman or cURL, the first steps is the same. Ensure that you have Python version 3.9 and the dependencies specified within the requirements.txt file installed. Then, run the application using the following command: 

```python app.py```

#### Postman 

**Generating A New API Key**

A new API key can be generated by: 

- Set request type to 'POST'
- URL: http://localhost:5000/generate_api_key
- Authorization: Basic Auth with admin credentials
- Body: x-www-form-urlencoded, key: tier, value: free

**Changing The API Key's Tier**

To change an API key's tier: 

- Request type 'POST'
- URL: http://localhost:5000/change_tier
- Authorization: Basic Auth with admin credentials
- Body: raw, format: JSON
```
{
  "api_key": "your_api_key",
  "new_tier": "builder"
}
```

**Accessing The Database**

To access data stored in the database, determine if you want to access the raw transaction, price, or metadata data. For example, the price route can be accessed by running the following steps:

- Request type: 'GET'
- URL: http://localhost:5000/prices
- Headers: API-Key, value: <your-API-key>
- Send the request

Similar steps can be taken to access the raw transaction and metadata information. 

#### CURL 

**Generating A New API Key**

To generate a new API key, run the following command: 

```
curl -X POST http://localhost:5000/generate_api_key -u admin_username:admin_password -d "tier=free"
```

Replace 'admin_username' and 'admin_password' with your actual admin credentials. 

**Changing The API Key's Tier**

The following can be ran to change an API key's tier: 

```
curl -X POST http://localhost:5000/change_tier \
-u admin_username:admin_password \
-H "Content-Type: application/json" \
-d '{"api_key": "your_api_key", "new_tier": "builder"}'
```

Where 'your_api_key" should be replaced by the address of a generated key. 

**Accessing The Database**

To access data stored in the database, determine if you want to access the raw transaction, price, or metadata data. For example, the price route can be accessed by running the following command: 

```
curl -X GET http://localhost:5000/prices -H "API-Key: your_api_key"
```

Similar commands can be ran to access the raw transaction and the metadata information. 

## Contributions
Contributions of any form are encouraged and appreciated. Please follow the "fork and pull" Git workflow if you would like to create a new feature:

1. Fork the repo on Github
2. Clone the repo onto your own machine
3. Create a new branch and commit any changes to this branch
4. Push your work to back up your fork
5. Submit a pull request and request review from jhuhnke IMPORTANT: Be sure to merge the lastest commit from upstream before submitting a pull request.
The more detailed the branch name and description of the pull request, the better! A thorough description of what you are adding to the codebase will help speed up the review process.

To report a bug or submit a feature request, please use the issues tab to open and submit an issue. The more detailed the bug report or feature request, the easier it is for me to integrate it into the application!

## Donations
Any donations are greatly appreciated and will be put torwards development costs. Extra donations will likely be used to buy the dev a coffee or a beer.

Solana address: EJXeG1MjjKr6dCkvdZfdFr4EtYo7XCciMKh8oynLTQis

## License 
This project is licensed under the MIT License - see the LICENSE file for details.

## Contact 
For any queries or suggestions, please reach out to me via email at huhnkejessica@gmail.com or on X: @web3_analyst

