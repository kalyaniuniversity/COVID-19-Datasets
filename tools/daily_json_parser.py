import requests

dataset = list()
unique_dates = list()

andaman_and_nicobar = dict()
andhra_pradesh = dict()
arunachal_pradesh = dict()
assam = dict()
bihar = dict()
chandigarh = dict()
chhattisgarh = dict()
daman_and_diu = dict()
delhi = dict()
dadra_and_nagar_haveli = dict()
goa = dict()
gujarat = dict()
himachal_pradesh = dict()
jammu_and_kashmir = dict()
haryana = dict()
jharkhand = dict()
karnataka = dict()
kerala = dict()
ladakh = dict()
lakshadweep = dict()
maharashtra = dict()
meghalaya = dict()
manipur = dict()
madhya_pradesh = dict()
mizoram = dict()
nagaland = dict()
odisha = dict()
punjab = dict()
puducherry = dict()
rajasthan = dict()
sikkim = dict()
telangana = dict()
tamil_nadu = dict()
tripura = dict()
uttar_pradesh = dict()
uttarakhand = dict()
west_bengal = dict()
total = dict()

andaman_and_nicobar['code'] = 'an'
andhra_pradesh['code'] = 'ap'
arunachal_pradesh['code'] = 'ar'
assam['code'] = 'as'
bihar['code'] = 'br'
chandigarh['code'] = 'ch'
chhattisgarh['code'] = 'ct'
daman_and_diu['code'] = 'dd'
delhi['code'] = 'dl'
dadra_and_nagar_haveli['code'] = 'dn'
goa['code'] = 'ga'
gujarat['code'] = 'gj'
himachal_pradesh['code'] = 'hp'
jammu_and_kashmir['code'] = 'jk'
haryana['code'] = 'hr'
jharkhand['code'] = 'jh'
karnataka['code'] = 'ka'
kerala['code'] = 'kl'
ladakh['code'] = 'la'
lakshadweep['code'] = 'ld'
maharashtra['code'] = 'mh'
meghalaya['code'] = 'ml'
manipur['code'] = 'mn'
madhya_pradesh['code'] = 'mp'
mizoram['code'] = 'mz'
nagaland['code'] = 'nl'
odisha['code'] = 'or'
punjab['code'] = 'pb'
puducherry['code'] = 'py'
rajasthan['code'] = 'rj'
sikkim['code'] = 'sk'
telangana['code'] = 'tg'
tamil_nadu['code'] = 'tn'
tripura['code'] = 'tr'
uttar_pradesh['code'] = 'up'
uttarakhand['code'] = 'ut'
west_bengal['code'] = 'wb'
total['code'] = 'tt'

andaman_and_nicobar['name'] = 'Andaman and Nicobar Islands'
andhra_pradesh['name'] = 'Andhra Pradesh'
arunachal_pradesh['name'] = 'Arunachal Pradesh'
assam['name'] = 'Assam'
bihar['name'] = 'Bihar'
chandigarh['name'] = 'Chandigarh'
chhattisgarh['name'] = 'Chhattisgarh'
daman_and_diu['name'] = 'Daman_and_diu'
delhi['name'] = 'Delhi'
dadra_and_nagar_haveli['name'] = 'Dadra and nagar haveli'
goa['name'] = 'Goa'
gujarat['name'] = 'Gujarat'
himachal_pradesh['name'] = 'Himachal Pradesh'
jammu_and_kashmir['name'] = 'Jammu and Kashmir'
haryana['name'] = 'Haryana'
jharkhand['name'] = 'Jharkhand'
karnataka['name'] = 'Karnataka'
kerala['name'] = 'Kerala'
ladakh['name'] = 'Ladakh'
lakshadweep['name'] = 'Lakshadweep'
maharashtra['name'] = 'Maharashtra'
meghalaya['name'] = 'Meghalaya'
manipur['name'] = 'Manipur'
madhya_pradesh['name'] = 'Madhya_pradesh'
mizoram['name'] = 'Mizoram'
nagaland['name'] = 'Nagaland'
odisha['name'] = 'Odisha'
punjab['name'] = 'Punjab'
puducherry['name'] = 'Puducherry'
rajasthan['name'] = 'Rajasthan'
sikkim['name'] = 'Sikkim'
telangana['name'] = 'Telangana'
tamil_nadu['name'] = 'Tamil Nadu'
tripura['name'] = 'Tripura'
uttar_pradesh['name'] = 'Uttar Pradesh'
uttarakhand['name'] = 'Uttarakhand'
west_bengal['name'] = 'West Bengal'
total['name'] = 'Total'

dataset.append(andaman_and_nicobar)
dataset.append(andhra_pradesh)
dataset.append(arunachal_pradesh)
dataset.append(assam)
dataset.append(bihar)
dataset.append(chandigarh)
dataset.append(chhattisgarh)
dataset.append(daman_and_diu)
dataset.append(delhi)
dataset.append(dadra_and_nagar_haveli)
dataset.append(goa)
dataset.append(gujarat)
dataset.append(himachal_pradesh)
dataset.append(jammu_and_kashmir)
dataset.append(haryana)
dataset.append(jharkhand)
dataset.append(karnataka)
dataset.append(kerala)
dataset.append(ladakh)
dataset.append(lakshadweep)
dataset.append(maharashtra)
dataset.append(meghalaya)
dataset.append(manipur)
dataset.append(madhya_pradesh)
dataset.append(mizoram)
dataset.append(nagaland)
dataset.append(odisha)
dataset.append(punjab)
dataset.append(puducherry)
dataset.append(rajasthan)
dataset.append(sikkim)
dataset.append(telangana)
dataset.append(tamil_nadu)
dataset.append(tripura)
dataset.append(uttar_pradesh)
dataset.append(uttarakhand)
dataset.append(west_bengal)
dataset.append(total)

raw_data = requests.get('https://api.covid19india.org/states_daily.json')
raw_json = raw_data.json()

for item in raw_json['states_daily']:
    if item['date'] not in unique_dates:
      unique_dates.append(item['date'])

for date in unique_dates:
    for item in raw_json['states_daily']:
        if date == item['date']:
            for state in dataset:
                if date not in state:
                    state[date] = dict()
                state[date][item['status']] = item[state['code']]

def needs_patch(date_to_fetch, state_code):

    if (date_to_fetch == '26-Mar-20' and state_code == 'ap') or (date_to_fetch == '16-Mar-20' and state_code == 'mp'):
        return True
    return False

def apply_patch(date_to_fetch, state_code):
    
    if date_to_fetch == '26-Mar-20' and state_code == 'ap':
        return {'Confirmed': '1', 'Recovered': '0', 'Deceased': '0'}
    if date_to_fetch == '16-Mar-20' and state_code == 'mp':
        return {'Confirmed': '0', 'Recovered': '0', 'Deceased': '0'}

def fetch_by_date_and_code(date_to_fetch, state_code):

    if(needs_patch(date_to_fetch, state_code)):
        return apply_patch(date_to_fetch, state_code)

    if date_to_fetch in unique_dates:
        for state in dataset:
            if state['code'] == state_code:
                if date_to_fetch in state:
                    return state[date_to_fetch]
    else :
        print('date does not exist')

def cumulative_datewise_data(date_to_fetch, state_code):

    should_stop = False

    for unique_date in unique_dates:

        if unique_date == date_to_fetch:
            should_stop = True
        
        print(unique_date, fetch_by_date_and_code(unique_date, state_code))

        if should_stop:
            break

def cumulative_data(date_to_fetch, state_code):

    should_stop = False
    cumulative_dict = dict()

    for unique_date in unique_dates:

        if unique_date == date_to_fetch:
            should_stop = True

        returned_dict = fetch_by_date_and_code(unique_date, state_code)
        
        for key in returned_dict:
            if key in cumulative_dict:
                cumulative_dict[key] += int(returned_dict[key])
            else:
                cumulative_dict[key] = int(returned_dict[key])

        if should_stop:
            break
    
    return cumulative_dict

def cumulative_series_datewise_data(date_to_fetch, state_code):

    should_stop = False
    cumulative_dict = dict()
    if date_to_fetch in unique_dates:
        for unique_date in unique_dates:

            if unique_date == date_to_fetch:
                should_stop = True
        
            print(unique_date, cumulative_data(unique_date, state_code))

            if should_stop:
                break
    else:
        print('date does not exist')

date_to_fetch = input('Enter date:')
state_code = input('Enter state code:')

# print(fetch_by_date_and_code(date_to_fetch, state_code))
cumulative_series_datewise_data(date_to_fetch, state_code)