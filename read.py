import time
from datetime import datetime, timezone, timedelta

import urllib.request as ur
import urllib.error as ue
import lxml.html as lh
import csv
from zoneinfo import ZoneInfo
from dateutil import tz

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive



url_1 = 'https://cyots.co.uk/ttssel.asp?id=3923&se7xtznvyp1z&sit=dsf&typ=L&pll=-50&plh=0&tbsl=3&tbsh=25&tnrl=2&tnrh=10&tpml=-8&tpmh=-3&cdcs=0&cdds=0&cdcd=1&cdao=0&rtall=1&rtp=1&rct=3'
url_2 = 'https://cyots.co.uk/ttssel.asp?id=3923&se7xtznvyp1z&sit=dsf&typ=L&pll=-50&plh=0&tdl=1760&tdh=9000&tbsl=3&tbsh=25&tpml=-8&tpmh=-3&cdcs=0&cdds=0&cdcd=1&cdao=0&rtall=1&rtp=1&rct=3'
url_3 = 'https://cyots.co.uk/ttssel.asp?id=3923&se7xtznvyp1z&sit=dsf&typ=L&nowl=1&nowh=50&tdl=1760&tdh=9000&lfl=-2&lfh=1&tbsl=3&tbsh=10&tnrl=2&tnrh=10&tpml=-8&tpmh=-3&rtall=1&rtp=1&rct=3'

file_1 = 'file_1.csv'
file_2 = 'file_2.csv'
file_3 = 'file_3.csv'

file_list = [file_1, file_2, file_3]
google_file_id = ['1y7cmPD2PXipbnySuLh-OCtXyOKywmL04', '1zNnZFE2esdLDGNYqpM1JazpFgeaP-OME', '1ON6-xTUo2Vyo720yaraYobct1Qam5m9U']

def get_ordinal_suffix(day):
    """Return the ordinal suffix for a given day."""
    if 10 <= day % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    return suffix

def write_to_csv(file, rows):
    """Write rows to a csv file."""
    with open(file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Provider', 'EventName', 'SelectionName', 'StartTime', 'BetType'])
        writer.writerows(rows)
        # for row in rows:
        #     if len(row) != 0:
        #         writer.writerow(row)
    

def authenticate_drive():
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile('credentials.json')  # Load previously saved credentials
    if gauth.credentials is None:
        gauth.LocalWebserverAuth()  # Authenticate if no credentials file found
        gauth.SaveCredentialsFile('credentials.json')  # Save new credentials
    elif gauth.credentials.invalid:
        gauth.LocalWebserverAuth()  # Re-authenticate if credentials are invalid
        gauth.SaveCredentialsFile('credentials.json')  # Save refreshed credentials
    return GoogleDrive(gauth)

def upload_to_remote_csv(i):
    """Upload csv files to remote server."""
    file_local = file_list[i]
    drive = authenticate_drive()
    file_id = google_file_id[i] 
    file = drive.CreateFile({'id': file_id})
    file.SetContentFile(file_local)
    file.Upload()
    print('File uploaded')


def change_to_utc(time):
    """Change local time to UTC time"""
    utc_time = str(int(time.split(':')[0]) - 1) + ':' + time.split(':')[1]
    return utc_time


def check_time(rows, file):
    """Check if time is in the future."""
    temp_row =[]
    for row in rows:
        start_time = datetime.strptime(row[3], '%d/%m/%Y %H:%M')
        start_time = start_time.replace(tzinfo=ZoneInfo('UTC'))
        print(start_time, 'start_time')
        if start_time > datetime.now(ZoneInfo('UTC')) and  start_time - datetime.now(ZoneInfo('UTC')) <= timedelta(minutes=2):
            temp_row.append(row)
        else:
            pass
    # with open(file, 'r') as f:
    #     reader = csv.reader(f)
    #     header = next(reader)
    #     for row in reader:
    #         start_time = datetime.strptime(row[3], '%d/%m/%Y %H:%M')
    #         start_time = start_time.replace(tzinfo=ZoneInfo('UTC'))
    #         print(start_time, 'start_time')
    #         if start_time > datetime.now(ZoneInfo('UTC')) and  start_time - datetime.now(ZoneInfo('UTC')) <= timedelta(minutes=250):
    #             temp_row.append(row)
    #         else:
    #             pass
    compare_row = []
    with open(file, 'r') as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            pass
        for row in reader:
            compare_row.append(row)

    print(temp_row, 'temp_row')
    print(compare_row, 'compare_row')
    if temp_row != compare_row:
        print('not equal')
        write_to_csv(file, temp_row)
        return 1
    return 0
    
    


def identify_event(short_name):
    """Return the full name of an event."""
    horse_racing_courses = {
    'Aint': 'Aintree', 'Ascot': 'Ascot', 'Ayr': 'Ayr', 'Bang': 'Bangor-on-Dee', 'Bath': 'Bath',
    'Bev': 'Beverley', 'Brig': 'Brighton', 'Carl': 'Carlisle', 'Cart': 'Cartmel', 'Catt': 'Catterick',
    'ChelmC': 'Chelmsford City', 'Chelt': 'Cheltenham', 'Chep': 'Chepstow', 'Chest': 'Chester',
    'Donc': 'Doncaster', 'Epsm': 'Epsom Downs', 'Extr': 'Exeter', 'Fake': 'Fakenham', 'FfosL': 'Ffos Las',
    'Font': 'Fontwell', 'Good': 'Goodwood', 'Ham': 'Hamilton', 'Hayd': 'Haydock', 'Here': 'Hereford',
    'Hex': 'Hexham', 'Hunt': 'Huntingdon', 'Kelso': 'Kelso', 'Kemp': 'Kempton', 'Leic': 'Leicester',
    'Ling': 'Lingfield', 'Ludl': 'Ludlow', 'MrktR': 'Market Rasen', 'Muss': 'Musselburgh', 'Newb': 'Newbury',
    'Newc': 'Newcastle', 'Newm': 'Newmarket', 'Newt': 'Newton Abbot', 'Nott': 'Nottingham', 'Perth': 'Perth',
    'Plump': 'Plumpton', 'Ponte': 'Pontefract', 'Redc': 'Redcar', 'Ripon': 'Ripon', 'Salis': 'Salisbury',
    'Sand': 'Sandown', 'Sedge': 'Sedgefield', 'Sthl': 'Southwell', 'Strat': 'Stratford', 'Taun': 'Taunton',
    'Thirsk': 'Thirsk', 'Towc': 'Towchester', 'Uttox': 'Uttoxeter', 'Warw': 'Warwick', 'Weth': 'Wetherby',
    'Winc': 'Wincanton', 'Wind': 'Windsor', 'Wolv': 'Wolverhampton', 'Worc': 'Worcester', 'Yarm': 'Yarmouth',
    'York': 'York', 'Ballin': 'Ballinrobe', 'Baelle': 'Bellewstown', 'Clon': 'Clonmel', 'Cork': 'Cork',
    'Curr': 'Curragh', 'DownR': 'Down Royal', 'DownP': 'Downpatrick', 'Dund': 'Dundalk', 'Fairy': 'Fairyhouse',
    'Gal': 'Galway', 'GowP': 'Gowran Park', 'Kilb': 'Kilbeggan', 'Killar': 'Killarney', 'Layt': 'Laytown',
    'Leop': 'Leopardstown', 'Lim': 'Limerick', 'List': 'Listowel', 'Naas': 'Naas', 'Navan': 'Navan',
    'Punch': 'Punchestown', 'Rosc': 'Roscommon', 'Sligo': 'Sligo', 'Thurl': 'Thurles', 'Tipp': 'Tipperary',
    'Tram': 'Tramore', 'Wex': 'Wexford'
    }
    return horse_racing_courses.get(short_name)

while True:
    time.sleep(10)
    try:
        html_1 = ur.urlopen(url_1).read()
        html_2 = ur.urlopen(url_2).read()
        html_3 = ur.urlopen(url_3).read()
    except ue.URLError:
        time.sleep(1)
        continue
    tree_1 = lh.fromstring(html_1)
    tree_2 = lh.fromstring(html_2)
    tree_3 = lh.fromstring(html_3)

    rows_1 = tree_1.xpath('//tr')    
    rows_2 = tree_2.xpath('//tr')
    rows_3 = tree_3.xpath('//tr')

    rows_list = [rows_1, rows_2, rows_3]

    provider_list = ['Josh_1', 'Josh_2', 'Josh_3']
    i = 0
    for rows in rows_list:
        print(i)
        if len(rows) == 0:
            print('No selection')
        new_row = []
        for row in rows:
            cells = row.xpath('.//td/text()')
            print(cells[0])
            date_time = f"{datetime.now(timezone.utc).strftime('%d/%m/%Y')} {change_to_utc(cells[0])}"
            day = datetime.now(timezone.utc).date().day
            month = datetime.now(timezone.utc).date().strftime('%b')
            suffix = get_ordinal_suffix(day)
            format_date = f"{day}{suffix} {month}"
            event = identify_event(cells[1])
            event_name = f"{event} {format_date}"
            new_row.append([provider_list[i], event_name or '', cells[2] or '', date_time or '', 'LAY'])
            print(date_time)
        # write_to_csv(file_list[i], new_row)
        print(new_row, end="/n/n")
        res = check_time(new_row, file_list[i])
        if res == 1:
            upload_to_remote_csv(i)
        i += 1

if __name___ == '__main__':
    pass