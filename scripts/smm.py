import requests
from requests.exceptions import ConnectionError
import csv
import time

# Define a function to export services to a CSV file
def export_to_csv(filename_prefix, services_per_site):
    for currency, services_list in services_per_site.items():
        filename = f"{filename_prefix}_{currency}.csv"
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Website', 'Service Name', 'Price', 'Min Quantity', 'Max Quantity', 'Dripfeed', 'Refill', 'Cancel', 'Category']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for site, services in services_list:
                website_name = site.split('/')[2].split('.')[0]
                for service_info in services:
                    rate = service_info['rate']
                    writer.writerow({
                        'Website': website_name,
                        'Service Name': service_info['name'],
                        'Price': rate,
                        'Min Quantity': service_info['min'],
                        'Max Quantity': service_info['max'],
                        'Dripfeed': service_info['dripfeed'],
                        'Refill': service_info['refill'],
                        'Cancel': service_info['cancel'],
                        'Category': service_info['category']
                    })

class Api:
    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.api_key = api_key

    def connect(self, post):
        try:
            response = requests.post(self.api_url, data=post)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()
        except (requests.exceptions.RequestException, ValueError) as e:
            print(f"Error connecting to {self.api_url}: {e}")
            return None  # Return None to indicate failure

    def order(self, data):
        post = {'key': self.api_key, 'action': 'add', **data}
        return self.connect(post)

    def status(self, order_id):
        post = {'key': self.api_key, 'action': 'status', 'order': order_id}
        return self.connect(post)

    # Diğer metodlar burada...

    def services(self):
        post = {'key': self.api_key, 'action': 'services'}
        return self.connect(post)

    def balance(self):
        post = {'key': self.api_key, 'action': 'balance'}
        return self.connect(post)

def get_api_info_from_url(url):
    response = requests.get(url)
    lines = response.text.splitlines()
    api_url = lines[0].strip()
    api_key = lines[1].strip()
    website_name = url.split('/')[2].split('.')[0]  # Web sitesi adını URL'den çıkar
    return api_url, api_key, website_name

def get_multiple_api_info_from_url(url):
    response = requests.get(url)
    lines = response.text.splitlines()
    api_info_list = []
    for i in range(0, len(lines), 2):
        api_url = lines[i].strip()
        api_key = lines[i + 1].strip()
        api_info_list.append((api_url, api_key))
    return api_info_list

# API URL ve anahtarını URL'den al
api_info_list = get_multiple_api_info_from_url("https://nizhenets.com/apiler.php")

# Tüm hizmetleri listesini toplamak için bir sözlük oluşturalım
services_per_site = {}

# Çekilemeyen ve çekilen siteleri ayırmak için listeler oluşturalım
failed_sites = []
successful_sites = []

total_service_count = 0  # Toplam servis sayısını tutmak için bir değişken

for api_url, api_key in api_info_list:
    # API'yi anahtar ve URL ile başlat
    api = Api(api_url, api_key)

    try:  # Add try-except block here
        # Deneme: Bakiyeden para birimini al
        retries = 3
        delay = 5
        for i in range(retries):
            try:
                balance_info = api.balance()

                # Check if balance_info is None before accessing its contents
                if balance_info is not None:
                    if 'error' in balance_info:
                        failed_sites.append(api_url)  # Çekilemeyen siteler listesine ekle
                        break  # Geçersiz anahtar veya URL varsa bir sonraki API'ye geç
                    elif 'currency' in balance_info:
                        currency = balance_info['currency']
                        print(f"Currency: {currency}")
                    else:
                        print("Currency information not available.")
                else:
                    failed_sites.append(api_url)  # Handle the case where balance_info is None
                    break  # Exit the loop if balance_info is None

                break  # Exit the retries loop if there are no exceptions
            except requests.exceptions.ConnectionError as e:
                print(f"Error: {e}. Retrying in {delay} seconds...")
                time.sleep(delay)
                if i == retries - 1:
                    print("Max retries exceeded. Failed to connect.")
                    failed_sites.append(api_url)
    except Exception as e:
        print(f"An error occurred while processing API {api_url}: {e}")

    if api_url in failed_sites:
        continue  # Eğer bağlantı kurulamadıysa bir sonraki API'ye geç

    # Tüm hizmetleri listele
    services = api.services()
    print("Available services:")
    for service_details in services:
        print(f"Service Name: {service_details['name']}")
        print(f"Type: {service_details['type']}")
        rate = f"{service_details['rate']} {currency}" if currency else service_details['rate']
        print(f"Rate: {rate}")
        print(f"Min: {service_details['min']}")
        print(f"Max: {service_details['max']}")
        print(f"Dripfeed: {service_details.get('dripfeed', 'N/A')}")
        print(f"Refill: {service_details.get('refill', 'N/A')}")
        print(f"Cancel: {service_details.get('cancel', 'N/A')}")
        print(f"Category: {service_details['category']}")
        print()

        # Her siteden kaç tane servis alındığını kaydet
        services_per_site.setdefault(currency, []).append((api_url, [{
            'name': service_details['name'],
            'rate': rate,
            'min': service_details['min'],
            'max': service_details['max'],
            'dripfeed': service_details.get('dripfeed', 'N/A'),
            'refill': service_details.get('refill', 'N/A'),
            'cancel': service_details.get('cancel', 'N/A'),
            'category': service_details['category']
        }]))
        total_service_count += 1

    successful_sites.append(api_url)  # Çekilen siteler listesine ekle

   # Toplam hizmet sayısı
    total_services = len(services)
    print(f"Total services: {total_services}")
    print("=" * 50)  # Ayırıcı çizgi

# Çekilen servislerin sayısını yazdır
print("Services per site:")
for currency, services_list in services_per_site.items():
    print(f"Currency: {currency}")
    for site, services in services_list:
        website_name = site.split('/')[2].split('.')[0]  # Web sitesi adını URL'den çıkar
        print(f"{website_name}: {len(services)} services")

# Çekilemeyen ve çekilen siteleri ayırt etmek için renk kodları tanımlayalım
RED = '\033[91m'
GREEN = '\033[92m'
RESET = '\033[0m'

# Başlığı yazdıralım
print(f"Total services retrieved: {total_service_count}")
print("Missing and Successful Services:")
print("=" * 50)

# Çekilen siteleri yazdıralım
for site in successful_sites:
    print(GREEN + f"Services retrieved from {site}" + RESET)

# Çekilemeyen siteleri yazdıralım
for site in failed_sites:
    print(RED + f"Failed to retrieve services from {site}" + RESET)

# CSV dosyalarını dışa aktar
export_to_csv('services', services_per_site)