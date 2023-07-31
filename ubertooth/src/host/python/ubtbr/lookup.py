#!/usr/bin/python3

import requests
import pandas as pd

# url = "https://mac-address-lookup1.p.rapidapi.com/static_rapid/mac_lookup/"
#
# querystring = {"query":"a4:83:e7"}
#
# headers = {
#     'x-rapidapi-key': "57430eb63emsh57befe4d7fb90d5p118528jsna49d5c10b90a",
#     'x-rapidapi-host': "mac-address-lookup1.p.rapidapi.com"
#     }
#
# response = requests.request("GET", url, headers=headers, params=querystring)
#
# result = response.json().get('result')[0]['name']
# print(result)

df = pd.read_csv('manufacturers.csv', usecols=['Decimal', 'Company'])
print(df.loc[df['Decimal'] == 3000]['Company'].item())
