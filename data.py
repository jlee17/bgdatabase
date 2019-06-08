import requests
from time import sleep

url = 'https://api.geekdo.com/xmlapi2/thing?id='

for num in range(165000, 167000):

    r = requests.get(url + str(num) + '&stats=1')
    print(num)
    sleep(2)

    with open('./data/' + str(num) + '.xml', 'wb') as datafile:
        datafile.write(r.content)