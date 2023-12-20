import random
import requests
import time
import json
from datetime import datetime

class TUI:
    alphabet = "ABCDEFGHJKLMNPQRSTVWXYZ"

    def __init__(self, value):
        self.value = value

    def is_valid(self):
        import re

        regex = re.compile(r"[0-9]{7}[A-Z]")
        if not regex.match(self.value):
            return False

        ctrl_key = sum(int(digit) * (len(self.value[:-1]) - index) for index, digit in enumerate(self.value[:-1])) % 23

        return self.value[-1] == list(TUI.alphabet)[ctrl_key]

def generate_company_numbers(starting_number, count):
    company_numbers = []
    for _ in range(count):
        number = str(starting_number) + ''.join(random.choices('0123456789', k=5))
        alphabet_index = sum(int(digit) * (len(number) - index) for index, digit in enumerate(number)) % 23
        ctrl_char = TUI.alphabet[alphabet_index]
        company_numbers.append(number + ctrl_char)
    return company_numbers

def check_validity(company_numbers):
    valid_numbers = []
    url = "https://fastapi-theta.vercel.app/tui"
    headers = {
        "x-api-key": "WzIsImhhbWVkIEhhd2FyaSJd"
    }
    for number in company_numbers:
        querystring = {"s": number}
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            valid_numbers.append(number)
        time.sleep(2)  # Introduce a delay of 1 second between requests to avoid overwhelming the API
    return valid_numbers

# Generate 100 company numbers starting with "17"
company_numbers = generate_company_numbers(16, 100)

# Check the validity of each company number and keep only valid ones
valid_numbers = check_validity(company_numbers)

# Generate a timestamp for the filename
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

# Construct the filename with the timestamp
json_filename = f'valid_numbers_{timestamp}.json'

# Print the valid company numbers
print("Valid Company Numbers:")
for number in valid_numbers:
    print(number)

# Save the valid company numbers to a JSON file
with open(json_filename, 'w') as json_file:
    json.dump(valid_numbers, json_file)
