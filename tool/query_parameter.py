import requests
import re
from urllib.parse import urljoin
params=[]
with open('Wordlists/common-param.txt','r') as f:
    for word in f:
        params.append(word)

def identification(endpoint, words):
    append=0
    new_param=''
    new_endpoint=''
    tot_new_endpoint=endpoint
    param_count=0
    m_requests=[]
    for word in words:
        word=word.strip()
        matches=re.findall(rf'\b\w*{word}\w*\b=\d+',endpoint)
        if bool(matches):
            for match in matches:
                sep_match=match.split('=')
                #num_match=re.search(r'\d+',match)
                append=int(sep_match[1])+1
                new_param=sep_match[0]+'='+str(append)
                new_endpoint=re.sub(match,new_param,endpoint)
                tot_new_endpoint=re.sub(r'\b'+match+r'\b',new_param,tot_new_endpoint)
                m_requests.append(new_endpoint)
                param_count+=1
    if param_count > 1:
        m_requests.append(tot_new_endpoint)
    if not tot_new_endpoint == endpoint:  
        return m_requests

def send_request(baseUrl, method, path, headers=None, body=None):
    url = urljoin(baseUrl, path)
    try:
        response = requests.request(method, url, headers=headers or {}, data=body, timeout=10)
        return response
    except requests.RequestException as e:
        print(url)
        print(f"\nError sending request {url}: {e}")
        return None

def if_bola(original_response, manipulated_response, o_path, m_path, ids):

    if original_response.status_code == 200 and manipulated_response.status_code == 200:
        for id in ids:
            id=id.strip()
            matches=re.findall(rf'\b\w*{id}\w*\b=\d+',o_path)
            if bool(matches):
                for match in matches:
                    sep_match=match.split('=')
                    original_id_value=re.search(r'[\'"]'+re.escape(sep_match[0])+r'[\'"]:\s*\d+',original_response.text)
                    manipulated_id_value=re.search(r'[\'"]'+re.escape(sep_match[0])+r'[\'"]:\s*\d+',manipulated_response.text)
                    if not original_id_value or not manipulated_id_value:
                        continue
                    elif id in manipulated_response.text and original_id_value.group(0) != manipulated_id_value.group(0):
                        print("="*100+"\n")
                        print(f"Original Response " + o_path + ":\b")
                        print(original_response.text + "\n")
                        print("-"*100+"\n")
                        print("Manipulated Response " + m_path + ":\b")
                        print(manipulated_response.text + "\n")
                        print("[!] Vulnerability Detected in " + sep_match[0])
                        print('[!] Reason:',original_id_value.group(0),manipulated_id_value.group(0))
                        print("="*100+"\n")
                    else:
                        continue
                        #print("[-] No vulnerability detected in " + sep_match[0])
            else:
                continue
                #print('[-] Valid Response but No Vulnerability Detected')

    elif original_response.text != manipulated_response.text:
        #print("[-] No Vulnerability Detected")
        return False
 
    elif manipulated_response.status_code == 403 or manipulated_response.status_code == 401:
        #print("Error: No Vulnerability Detected")
        return False
    else:
        #print("Default - No Vulnerability Detected")
        return False


def test_query_bola(baseUrl, captured_requests, auth_type, auth):    
    for req in captured_requests:
        if auth_type:
            req['headers'][auth_type] = auth
        m_endpoints=identification(req['path'], params)
        if m_endpoints is None:
            #print(f'\n[-] {req['path']}: endpoint did not match criteria')
            continue
        else:
            for m_endpoint in m_endpoints:
                try:
                    original_response=send_request(baseUrl, req['method'], req['path'], req['headers'], req['body'])
                    manipulated_response=send_request(baseUrl, req['method'], m_endpoint, req['headers'], req['body'])
                    if not original_response or not manipulated_response:
                            continue
                    if_bola(original_response, manipulated_response, req['path'], m_endpoint,params)
                except requests.exceptions.ConnectTimeout as err:
                    print(f'HOST UNREACHABLE: {baseUrl}{req['path']}')
                # except Exception as e:
                #     print("Something went wrong...")
