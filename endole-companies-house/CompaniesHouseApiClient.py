import requests
import base64
import xlsxwriter

def companies_house_api_auth():
    sample_string = 'cdcfe37b-b629-4652-a1d1-665e6aa0e63b:'
    sample_string_bytes = sample_string.encode("ascii")

    base64_bytes = base64.b64encode(sample_string_bytes)
    base64_string = base64_bytes.decode("ascii")
    return base64_string



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

    return json


def make_xlsx(json):
    workbook = xlsxwriter.Workbook('companies_house.xlsx')
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({'bold': True})
    worksheet.write('A1', 'Company Name', bold)
    worksheet.write('A2', json['company_name'])

    worksheet.write('B1', 'Registration Number', bold)
    worksheet.write('B2', json['company_number'])

    worksheet.write('C1', 'Status', bold)
    worksheet.write('C2', json['company_status'])

    worksheet.write('D1', 'Address', bold)
    worksheet.write('D2', json['registered_office_address']['address_line_1'] + "," +
                    json['registered_office_address']['address_line_2'] + "," +
                    json['registered_office_address']['locality'] + "," +
                    json['registered_office_address']['postal_code'] + "," +
                    json['registered_office_address']['country'])

    worksheet.write('E1', 'Accounts Made up to date', bold)
    worksheet.write('E2', json['accounts']['next_made_up_to'])

    worksheet.write('F1', 'Confirmation Made up to date', bold)
    worksheet.write('F2', json['confirmation_statement']['next_made_up_to'])

    workbook.close()


if __name__ == "__main__":
    json = companies_house_data()
    make_xlsx(json)
