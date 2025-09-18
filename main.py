import argparse
from bfla_delete import test_bfla
from numerical_value import test_num_bola
from query_parameter  import test_query_bola
from server_header import test_server_header
from  extract import parse_input_file

if __name__=='__main__':
    parser=argparse.ArgumentParser(description='API Automation Tool')
    parser.add_argument('-u', dest='baseUrl', required=True, help='The host address')
    parser.add_argument('-i', dest='har_file', required=True, help='Har File Location')
    parser.add_argument('--auth', dest='auth_header', required=False, help='The Authorization Header')

    args=parser.parse_args()

    baseUrl=args.baseUrl
    har_file=args.har_file
    auth_header=args.auth_header
    if auth_header:
        sep_auth=auth_header.split(': ')
        auth_type=sep_auth[0]
        auth=sep_auth[1]
    else:
        auth_type=None
        auth=None

    captured_requests=parse_input_file(har_file)
    
    print("\nChecking for BOLA....\n")
    test_num_bola(baseUrl,captured_requests, auth_type, auth)
    test_query_bola(baseUrl,captured_requests, auth_type, auth)
    print("\nChecking for BFLA....\n")
    test_bfla(baseUrl,captured_requests, auth_type, auth)
    print("\nChecking for Security Misconfiguration....\n")
    test_server_header(baseUrl,captured_requests)