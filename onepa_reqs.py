import requests
import datetime
import time 
import random

from   bs4 import BeautifulSoup

cc_list = ['ACE The Place CC',
    'Anchorvale CC',
    'Ayer Rajah CC',
    'Bedok CC',
    'Bishan CC',
    'Boon Lay CC',
    'Braddell Heights CC',
    'Bukit Batok CC',
    'Bukit Merah CC',
    'Bukit Panjang CC',
    'Bukit Timah CC',
    'Buona Vista CC',
    'Cairnhill CC',
    'Canberra CC',
    'Changi Simei CC',
    'Chong Pang CC',
    'Chua Chu Kang CC',
    'Clementi CC',
    'Eunos CC',
    'Gek Poh Ville CC',
    'Geylang Serai CC',
    'Geylang West CC',
    'Henderson CC',
    'Hong Kah North CC',
    'Hougang CC',
    'Hwi Yoh CC',
    'Jalan Besar CC',
    'Joo Chiat CC',
    'Jurong Green CC',
    'Jurong Spring CC',
    'Kallang CC',
    'Kampong Glam CC',
    'Kampong Kembangan CC',
    'Kampong Ubi CC',
    'Keat Hong CC',
    'Kebun Baru CC',
    'Kim Seng CC',
    'Leng Kee CC',
    'MacPherson CC',
    'Marine Parade CC',
    'Marsiling CC',
    'Nanyang CC',
    'Nee Soon East CC',
    'Nee Soon South CC',
    'OUR TAMPINES HUB CC',
    'Pasir Ris Elias CC',
    'Paya Lebar Kovan CC',
    'Pek Kio CC',
    'Potong Pasir CC',
    'Punggol 21 CC',
    'Queenstown CC',
    'Radin Mas CC',
    'Sembawang CC',
    'Siglap CC',
    'Taman Jurong CC',
    'Tampines Changkat CC',
    'Tampines North CC',
    'Tampines West CC',
    'Tanglin CC',
    'Tanjong Pagar CC',
    'Teck Ghee CC',
    'Telok Blangah CC',
    'The Frontier CC',
    'Thomson CC',
    'Tiong Bahru CC',
    'Toa Payoh Central CC',
    'Toa Payoh East CC',
    'Toa Payoh South CC',
    'West Coast CC',
    'Whampoa CC',
    'Woodlands CC',
    'Woodlands Galaxy CC',
    'Yew Tee CC',
    'Yio Chu Kang CC',
    'Yuhua CC',
    'Zhenghua CC'
]

def get_cc_hash_mapping():
    url = 'https://www.onepa.sg/facilities/4490ccmcpa-bm'
    with requests.session() as s:
        s.headers['user-agent'] = 'Mozilla/5.0'
        r = s.get(url)
        data = {}
        soup = BeautifulSoup(r.content, 'html.parser')
        state = { tag['name']: tag['value'] for tag in soup.select('input[name^=__]')}
    return {el.text: el['value'] for el in soup.select('option')}

CC_HASH_MAPPING = get_cc_hash_mapping()

def check_cc_for_day(cc, target_date):
    cc_hash = CC_HASH_MAPPING[cc]
    if not isinstance(target_date, str):
        target_date = target_date.strftime('%d/%m/%Y')
    url = 'https://www.onepa.sg/facilities/4490ccmcpa-bm'
    with requests.session() as s:
        s.headers['user-agent'] = 'Mozilla/5.0'
        r = s.get(url)
        data = {}
        soup = BeautifulSoup(r.content, 'html.parser')
        state = { tag['name']: tag['value'] for tag in soup.select('input[name^=__]')}
        data.update(state)
        data['__EVENTTARGET'] = 'content_0$ddlFacilityLocation'
        data['content_0$tbDatePicker'] = target_date
        data['content_0$ddlFacilityLocation'] = cc_hash
        #  New request, with specified cc and datetime
        r = s.post(url, data=data)
        soup_new = BeautifulSoup(r.content, 'html.parser')
        slot_status = soup_new.select('span[class^=slots]')
        slot_status = [el['class'][1] for el in slot_status]
        slot_names = [el.text for el in soup_new.select('div[class^=slots]') if 'AM' in el.text or 'PM' in el.text]
        slot_status_dict = {}
        for i in range(len(slot_names)):
            if slot_status[i] in ['normal', 'peak']:
                slot_status_dict[slot_names[i].replace(' ','')] = slot_status[i]
        return slot_status_dict

def check_date_availability(target_date):
    if not isinstance(target_date, str):
        target_date = target_date.strftime('%d/%m/%Y')
    cc_availability = {}
    url = 'https://www.onepa.sg/facilities/4490ccmcpa-bm'
    with requests.session() as s:
        r = s.get(url)
        s.headers['user-agent'] = 'Mozilla/5.0'
        data = {}
        soup = BeautifulSoup(r.content, 'html.parser')
        for i, cc in enumerate(cc_list):
            print(f'{i/len(cc_list)*100:.1f}% done...')
            cc_hash = CC_HASH_MAPPING[cc]
            state = { tag['name']: tag['value'] for tag in soup.select('input[name^=__]')}
            data.update(state)
            data['__EVENTTARGET'] = 'content_0$ddlFacilityLocation'
            data['content_0$tbDatePicker'] = target_date
            data['content_0$ddlFacilityLocation'] = cc_hash
            #  New request, with specified cc and datetime
            r = s.post(url, data=data)
            soup = BeautifulSoup(r.content, 'html.parser')
            slot_status = soup.select('span[class^=slots]')
            slot_status = [el['class'][1] for el in slot_status]
            slot_names = [el.text for el in soup.select('div[class^=slots]') if 'AM' in el.text or 'PM' in el.text]
            slot_status_dict = {}
            for i in range(len(slot_names)):
                if slot_status[i] in ['normal', 'peak']:
                    slot_status_dict[slot_names[i].replace(' ','')] = slot_status[i]
            time.sleep(random.random()/10)
            if len(list(slot_status_dict.keys())) != 0:
                cc_availability[cc] = slot_status_dict
            # if cc == 'Ayer Rajah CC':
            #     break
    return cc_availability

def check_cc_availability(cc):
    date_availability = {}
    url = 'https://www.onepa.sg/facilities/4490ccmcpa-bm'
    cc_hash = CC_HASH_MAPPING[cc]
    with requests.session() as s:
        r = s.get(url)
        s.headers['user-agent'] = 'Mozilla/5.0'
        data = {}
        soup = BeautifulSoup(r.content, 'html.parser')
        for i in range(14):
            print(f'{i/14*100:.1f}% done...')
            target_date = (datetime.datetime.now()+datetime.timedelta(days=i)).strftime('%d/%m/%Y')
            state = { tag['name']: tag['value'] for tag in soup.select('input[name^=__]')}
            data.update(state)
            data['__EVENTTARGET'] = 'content_0$ddlFacilityLocation'
            data['content_0$tbDatePicker'] = target_date
            data['content_0$ddlFacilityLocation'] = cc_hash
            #  New request, with specified cc and datetime
            r = s.post(url, data=data)
            soup = BeautifulSoup(r.content, 'html.parser')
            slot_status = soup.select('span[class^=slots]')
            slot_status = [el['class'][1] for el in slot_status]
            slot_names = [el.text for el in soup.select('div[class^=slots]') if 'AM' in el.text or 'PM' in el.text]
            slot_status_dict = {}
            for i in range(len(slot_names)):
                if slot_status[i] in ['normal', 'peak']:
                    slot_status_dict[slot_names[i].replace(' ','')] = slot_status[i]
            time.sleep(random.random()/10)
            if len(list(slot_status_dict.keys())) != 0:
                date_availability[target_date] = slot_status_dict
    return date_availability