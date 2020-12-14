from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from collections import deque
import random

# If modifying these scopes, delete the file token.pickle.

# read/write
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.

# fa20bros spreadsheet
SPREADSHEET_ID = '1NvMdLi3mPeO8WWEH0cC_yMCakPRq8IYq67X-0Fb4iJU'

# exclude = ['Daniel Chen', 'Oh Byung Kwon']
exclude = []

odd_bro = ''
odd_group = {}


def main():
    service = login()  # login and read in spreadsheet
    new_pairs, new_week = new_pairing(service)
    update_contacts(new_pairs, new_week, service)
    odd_bro = ''
    odd_group.clear()
    exclude.clear()


def update_contacts(new_pairs, week, service):
    contact_range = cell_range('Form Responses', 'A2', 'F')
    contact_info = read_spreadsheet(service, contact_range)
    info = {}
    for c in contact_info:
        if (len(c) < 6):
            c.append("")
    for c in contact_info:
        info[c[1]] = [c[1], c[2], c[5]]
    current_range = cell_range('This_Week', 'A1', 'D')
    updated_contact = []
    for p in new_pairs:
        if (p[1] == 'n/a'):
            updated_contact.append([p[0], 'n/a', 'n/a', 'n/a'])
        else:
            if (p[0] not in odd_group):
                updated_contact.append([p[0]] + info[p[1]])
            else:
                odd_info = []
                first_bro = odd_group[p[0]][0]
                second_bro = odd_group[p[0]][1]
                for i in range(len(info[first_bro])):
                    odd_info.append(info[first_bro][i] + ", " + info[second_bro][i])
                updated_contact.append([p[0]] + odd_info)


    header = ['Week of', week, 'Phone #', 'Comments']
    update_spreadsheet([header] + updated_contact, service, current_range)


def new_pairing(service):
    global odd_bro
    SHEET_RANGE = cell_range('All_Pairs', 'A1', 'AZ')

    values = read_spreadsheet(service, SHEET_RANGE)

    weeks = values[0]

    brothers = []

    num_week = len(values[1]) - 2  # hidden row to record weeks

    values = values[2:]

    for v in values:
        if (len(v) > num_week + 2):
            exclude.append(v[0])

    for v in values:
        if (v[1] not in exclude):
            brothers.append(v[1])  # get all brothers (hidden column that stores initial pairings)

    if (len(exclude) % 2 == 1):  # odd number, select random brother
        odd_bro = random.choice(brothers)
        brothers.remove(odd_bro)

    brothers = rr_rotate(brothers, num_week)  # do round robin rotation

    pairs = rr_pairs(brothers)  # pair up brothers

    for i in range(len(pairs)):  # add new column for new pairings
        if (values[i][0] not in exclude):
            values[i].append(pairs[i][1])

    week_counter = ['test'] * (num_week + 3)
    values = [weeks] + [week_counter] + values

    update_spreadsheet(values, service, SHEET_RANGE)

    exclude.clear()

    return pairs, weeks[num_week + 2]


# performs round robin rotation on brothers. Number of rotations depends on the week
# round robin rotation fixes first brother, rotates all others
# example with 4 bros: (1, 2), (3, 4) -> (1, 3), (4, 2) -> (1, 4), (2, 3)
def rr_rotate(brothers, num_week):
    for i in range(num_week):  # rotate based on which week it is

        mid = int(len(brothers) / 2)  # split into two halves
        bros1 = brothers[:mid]
        bros2 = brothers[mid:]

        first_bro_1 = bros1[0]  # store edge bros
        last_bro_2 = bros2[-1]

        bros1 = deque(bros1)  # deque for rotation
        bros2 = deque(bros2)

        bros1.rotate(-1)
        bros2.rotate(1)

        bros1 = list(bros1)
        bros2 = list(bros2)

        bros1[-1] = last_bro_2  # update edge bros
        bros2[0] = bros1[0]
        bros1[0] = first_bro_1

        brothers = bros1 + bros2  # combine halves

    return brothers


# creates pairings after round robin rotation
def rr_pairs(brothers):
    mid = int(len(brothers) / 2)  # split up brothers into two halves
    bros1 = brothers[:mid]
    bros2 = brothers[mid:]

    pairs = list(zip(bros1, bros2))  # pair up brothers

    if (odd_bro != ''):
        odd_pair = random.choice(pairs)
        pairs.remove(odd_pair)
        odd_group[odd_bro] =  [odd_pair[0], odd_pair[1]]
        odd_group[odd_pair[0]] = [odd_pair[1], odd_bro]
        odd_group[odd_pair[1]] = [odd_bro, odd_pair[0]]

    dup = []
    for p in pairs:
        dup.append((p[1], p[0]))  # duplicate in reverse

    if (odd_bro != ''):
        pairs.append((odd_bro, odd_pair[0] + ", " + odd_pair[1]))
        pairs.append((odd_pair[0], odd_pair[1] + ", " + odd_bro))
        pairs.append((odd_pair[1], odd_bro + ", " + odd_pair[0]))

    for e in exclude:
        dup.append((e, 'n/a'))

    pairs = pairs + dup
    pairs.sort()  # sort alphabetically

    return pairs


def login():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('sheets', 'v4', credentials=creds)
    # Call the Sheets API

    return service


def read_spreadsheet(service, sheet_range):
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=sheet_range).execute()
    # get values from range above, ignores rows with no data
    values = result.get('values', [])
    return values


def update_spreadsheet(new_values, service, sheet_range):
    body = {
        'values': new_values
    }
    result = service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID, range=sheet_range,
        valueInputOption='USER_ENTERED', body=body).execute()
    print('{0} cells updated.'.format(result.get('updatedCells')))


def cell_range(sheet, start, end):
    return sheet + "!" + start + ":" + end


if __name__ == '__main__':
    main()
