import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def main():
    scope = ['https://spreadsheets.google.com/feeds']
    doc_id = '1ORQg_26MJNrFisFxMfK_p8PcsrDuIXu6TNbd3bm1gTo'
    path = os.path.expanduser("../conf/API Project-476fa123229c.json")

    credentials = ServiceAccountCredentials.from_json_keyfile_name(path, scope)
    client = gspread.authorize(credentials)
    gfile   = client.open_by_key(doc_id)
    worksheet  = gfile.sheet1
    records = worksheet.get_all_values()
    for record in records:
        print(record)

if __name__ == '__main__':
    main()