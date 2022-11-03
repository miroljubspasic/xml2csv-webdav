import os
from webdav4.client import Client
from os.path import basename
from datetime import datetime
from dotenv import load_dotenv
import xmltodict
import csv


def main():
    load_dotenv()

    url = os.environ["WEBDAV_URL"]
    auth = (
     os.environ["WEBDAV_USER"],
     os.environ["WEBDAV_PASS"]
    )
    customers_path = os.environ["CUSTOMERS_REMOTE"]
    customers_local = os.environ["CUSTOMERS_LOCAL"]

    # print(url)
    # print(auth)
    # print(customers_path)
    # print(customers_local)
    # exit(1);
    client = Client(base_url=url, auth=auth)
    remoteCustomersList = client.ls(path=customers_path, detail=True)

    xmlFiles = list(filter(lambda f: f['content_type'] == "application/xml", remoteCustomersList))
    csvFiles = list(filter(lambda f: f['content_type'] == "text/csv", remoteCustomersList))

    returnList = []
    for xmlFile in xmlFiles:
        remoteFilePath = xmlFile['href']
        localFilePath = customers_local+basename(xmlFile['href'])
        client.download_file(from_path=remoteFilePath,
                             to_path=localFilePath,
                             callback=(returnList.append(localFilePath)))

    for xmlFile in returnList:
        resultData = []
        with open(xmlFile) as xml_file:
            data_dict = xmltodict.parse(xml_file.read())
            for customerData in data_dict.get('customers').get('customer'):
                delivery_address = None
                zip_code = None
                country = None
                gender = None
                client_status = None
                number_of_paid = 0
                birthdate = None
                if customerData.get('profile').get('birthday') is not None:
                    birthdate = datetime.strptime(customerData.get('profile').get('birthday'), '%Y-%m-%dZ').strftime("%Y-%m-%d")

                if customerData.get('profile').get('gender') is not None:
                    if int(customerData.get('profile').get('gender')) == 0:
                        gender = 'female'
                    elif int(customerData.get('profile').get('gender')) == 1:
                        gender = 'male'

                if customerData.get('addresses') is not None and type(customerData.get('addresses').get('address')) is list:
                    for addr in customerData.get('addresses').get('address'):
                        if addr.get('@preferred') == 'true':
                            delivery_address = addr.get('address1')
                            zip_code = addr.get('postal-code')
                            country = addr.get('country-code')
                elif customerData.get('addresses') is not None:
                    delivery_address = customerData.get('addresses').get('address').get('address1')
                    zip_code = customerData.get('addresses').get('address').get('postal-code')
                    country = customerData.get('addresses').get('address').get('country-code')
                if customerData.get('profile').get('custom-attributes') is not None:
                    for customAttr in customerData.get('profile').get('custom-attributes').get('custom-attribute'):
                        if type(customAttr) == dict and customAttr.get('@attribute-id') == 'pl_customerStatus':
                            client_status = customAttr.get('value')
                            if type(client_status) == list:
                                client_status = ', '.join(client_status)
                        if type(customAttr) == dict and customAttr.get('@attribute-id') == 'pl_paidBoxesNbr':
                            number_of_paid = customAttr.get('#text')

                resultData.append({
                    'firstname': customerData.get('profile').get('first-name'),
                    'lastname': customerData.get('profile').get('last-name'),
                    'date of birth': birthdate,
                    'delivery address': delivery_address,
                    'zip code': zip_code,
                    'country': country,
                    'id client': customerData.get('@customer-no'),
                    'mail': customerData.get('profile').get('email'),
                    'telephone number': customerData.get('profile').get('phone-home'),
                    'gender': gender,
                    'client status': client_status,
                    'fidelity points': None,
                    'fidelity status': None,
                    'number of paid boxes': number_of_paid
                })

            csvFile = xmlFile.replace('.xml', '.csv')

            with open(basename(csvFile), 'w', encoding='UTF8') as f:
                writer = csv.writer(f)
                writer.writerow(resultData[0].keys())

                for row in resultData:
                    writer.writerow(row.values())

                client.upload_file(from_path=basename(csvFile),
                                   to_path=customers_path+basename(csvFile),
                                   overwrite=True)
                os.remove(basename(csvFile))
                os.remove(xmlFile)
