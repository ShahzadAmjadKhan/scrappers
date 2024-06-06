import requests
import base64


def endole_api_auth():
    sample_string = '22468:NskjDa849YA2N1ITyeoYMh2snRbg2PTQ'
    sample_string_bytes = sample_string.encode("ascii")

    base64_bytes = base64.b64encode(sample_string_bytes)
    base64_string = base64_bytes.decode("ascii")
    return base64_string

def companies_house_api_auth():
    sample_string = 'cdcfe37b-b629-4652-a1d1-665e6aa0e63b:'
    sample_string_bytes = sample_string.encode("ascii")

    base64_bytes = base64.b64encode(sample_string_bytes)
    base64_string = base64_bytes.decode("ascii")
    return base64_string


def endole_company_data():
    url = 'https://api.endole.co.uk/company/{}?sandbox=true'.format('00445790')
    header = {"Authorization": "Basic " + endole_api_auth()}
    requests.get(url, headers=header)
    response = requests.get(url, headers=header)
    print(response.status_code)
    json = response.json()
    print("company name: {}".format(json['company_name']))
    print("registration number: {}".format(json['external_registration_number']))
    print("company status: {}".format(json['company_status']))
    print("registered address: {}".format(json['registered_office_address']['address_line_1'] + "," +
                                          json['registered_office_address']['address_line_2'] + "," +
                                          json['registered_office_address']['locality'] + "," +
                                          json['registered_office_address']['po_box'] + "," +
                                          json['registered_office_address']['postal_code'] + "," +
                                          json['registered_office_address']['region'] + "," +
                                          json['registered_office_address']['country']))
    print("company type: {}".format(json['subtype']))

def pretty_print_POST(req):
    """
    At this point it is completely built and ready
    to be fired; it is "prepared".

    However pay attention at the formatting used in
    this function because it is programmed to be pretty
    printed and may differ from the actual request.
    """
    print('{}\n{}\r\n{}\r\n\r\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\r\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
        ))

def companies_house_data():
    url = 'https://api-sandbox.company-information.service.gov.uk/company/{}'.format('34351932')
    header = {"Authorization": "Basic " + companies_house_api_auth()}
    response = requests.get(url, headers=header)
    json = response.json()
    print(json)
    print("company name: {}".format(json['company_name']))
    print("registration number: {}".format(json['company_number']))
    print("company status: {}".format(json['company_status']))
    print("registered address: {}".format(json['registered_office_address']['address_line_1'] + "," +
                                          json['registered_office_address']['address_line_2'] + "," +
                                          json['registered_office_address']['locality'] + "," +
                                          json['registered_office_address']['postal_code'] + "," +
                                          json['registered_office_address']['country']))
    print("accounts made up to date: {}".format(json['accounts']['next_made_up_to']))
    print("confirmation made up to date: {}".format(json['confirmation_statement']['next_made_up_to']))


if __name__ == "__main__":
    # endole_company_data()
    companies_house_data()
