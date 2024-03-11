import requests
import argparse
import json
import yaml

BANNER = r"""
███████╗███╗   ██╗██╗███████╗███████╗ ██████╗ ██╗     ██╗
██╔════╝████╗  ██║██║██╔════╝██╔════╝██╔═══██╗██║     ██║
███████╗██╔██╗ ██║██║█████╗  █████╗  ██║   ██║██║     ██║
╚════██║██║╚██╗██║██║██╔══╝  ██╔══╝  ██║▄▄ ██║██║     ╚═╝
███████║██║ ╚████║██║██║     ██║     ╚██████╔╝███████╗██╗
╚══════╝╚═╝  ╚═══╝╚═╝╚═╝     ╚═╝      ╚══▀▀═╝ ╚══════╝╚═╝
                                                         """

parser = argparse.ArgumentParser(description="GraphQL Endpoint Checker")
parser.add_argument("-u", "--url", dest="url", required=True, help="Specify the target URL")
parser.add_argument("-t", "--timeout", dest="timeout", type=int, default=5, help="Specify request timeout in seconds")
parser.add_argument("-o", "--output-format", dest="output_format", default="json", choices=["json", "yaml"], help="Specify output format")
args = parser.parse_args()
target_url = args.url

available_endpoints = [
    '/graphql',
    '/graphiql',
    '/graphql.php',
    '/graphql/console',
    '/api',
    '/api/graphql',
    '/graphql/api',
    '/graphql/graphql'
]

introspection_queries = [
    '{__schema{types{name,fields{name,args{name,description,type{name,kind,ofType{name,kind}}}}}}}',
    'query={__schema{types{name,fields{name}}}}'
]


def check_url(url):
    timeout = args.timeout
    try:
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        
        if not url.endswith('/'):
            url += '/'

        response = requests.head(url, timeout=timeout)
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        return False


def check_graphql(url):
    valid_new_urls = [url + endpoint for endpoint in available_endpoints if check_url(url + endpoint)]
    return valid_new_urls


def check_introspection(urls):
    introspection_results = {}

    for url in urls:
        url_with_parameter = url + '?query='

        for query in introspection_queries:
            full_url = url_with_parameter + query
            response = requests.get(full_url)

            if response.status_code == 200:
                try:
                    formatted_data = response.json()

                    if args.output_format == "json":
                        formatted_result = json.dumps(formatted_data, indent=2)
                    elif args.output_format == "yaml":
                        formatted_result = yaml.dump(formatted_data, default_flow_style=False)
                    else:
                        formatted_result = "Invalid output format"

                    introspection_results[full_url] = formatted_result
                except json.JSONDecodeError:
                    introspection_results[full_url] = "Invalid JSON response"
            else:
                introspection_results[full_url] = f"Request failed with status code: {response.status_code}"

    return introspection_results


def main():
    print(BANNER)

    if check_url(target_url):
        print(f"\nValid URL: {target_url}")
    else:
        print(f"\nNot a valid URL: {target_url}")

    valid_graphql_urls = check_graphql(target_url)

    if valid_graphql_urls:
        print("\nValid GraphQL URLs:")
        for url in valid_graphql_urls:
            print(f"  - {url}")

        introspection_results = check_introspection(valid_graphql_urls)

        print("\nIntrospection Results:")
        for url, result in introspection_results.items():
            print(f"\n{url}\n{result}\n")

    else:
        print("\nNo valid GraphQL URLs found.")


if __name__ == "__main__":
    main()
