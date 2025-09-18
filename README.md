# AutoPwn API ⚡

**AutoPwn API** is an automation framework for **API security testing**, built to help researchers and developers identify vulnerabilities in RESTful and GraphQL APIs.  
The tool is designed to speed up pentesting by automating common checks and hunting for flaws with minimal manual effort.

### Capabilities
- Supports **REST APIs**  
- Accepts **HAR files** as input for testing  
- Implements **4 test cases** so far (with more being added regularly)  
- Supports authorized testing — allows sending custom authorization headers (e.g., Authorization: Bearer <token>) with requests.

### Upcoming
- Support for more input formats (Swagger/OpenAPI specifications, Postman collections) 
- Continuous addition of **new test cases** (aiming for broad coverage of OWASP API Top 10 + business logic flaws)  
- Better post test result view
- Various Authentication handling (OAuth, API Keys)  

⚠️ **Work in Progress**: This project is actively under development. Expect frequent updates, new features, and major improvements in the near future.

# 🛠️ Usage

Run the tool from with `main.py` in the `tool` directory.

Basic command-line syntax:

```
python3 main.py [-h] -u BASEURL -i HAR_FILE [--auth AUTH_HEADER]
```

## Flags
```
-h
Show help/usage information.

-u BASEURL
Base URL of the target API (e.g., https://api.example.com).

-i HAR_FILE
Path to the HAR file to use as input (required).

--auth AUTH_HEADER
Optional custom authorization header string to attach to requests (e.g., "Authorization: Bearer <token>").
```
## Examples
### Basic test (no auth)
```
python3 main.py -u https://api.example.com -i samples/session.har
```

### Authorized testing
If you want to do  authorization with a bearer token, then:
```
python3 main.py -u https://api.example.com -i samples/session.har --auth "Authorization: Bearer <bearer_token>"
```

### Show help
```bash
python3 main.py -h
```
