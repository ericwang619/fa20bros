from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from collections import deque
import sys

# read/write permission
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

SPREADSHEET_ID = ''

def main(offset=0):
    service = login()  # login and read in spreadsheet
    new_pairs, new_week = new_pairing(service, offset)
    update_contacts(new_pairs, new_week, service)


# pull list of brothers from google form responses
def get_brothers(service):
    SHEET_RANGE = cell_range('Form Responses', 'B2', 'D')
    responses = read_spreadsheet(service, SHEET_RANGE)
    brothers = []
    for r in responses:
        brothers.append(r[0])

    return brothers


# generate new pairs for this week
def new_pairing(service, offset):
    brothers = get_brothers(service)

    SHEET_RANGE = cell_range('All_Pairs', 'A1', 'AZ')
    all_pairs = read_spreadsheet(service, SHEET_RANGE)


    if (len(all_pairs) == 1):
        sorted_brothers = sorted(brothers)
        for b in sorted_brothers:
            all_pairs.append([b])

    num_week = len(all_pairs[1])

    weeks = all_pairs[0]   # week header
    all_pairs = all_pairs[1:]

    (bros1, bros2) = rr_rotate(brothers, num_week + offset)  # do round robin rotation

    pairs = rr_pairs(bros1, bros2)  # pair up brothers

    for i in range(len(pairs)):  # add new column for new pairings
        all_pairs[i].append(pairs[i][1])

    all_pairs = [weeks] + all_pairs
    update_spreadsheet(all_pairs, service, SHEET_RANGE)

    return pairs, weeks[num_week]


# performs round robin rotation on brothers. Number of rotations depends on the week
# round robin rotation fixes first brother, rotates all others
# example with 4 bros: [1, 2], [3, 4] -> [1, 3], [4, 2] -> [1, 4], [2, 3]
def rr_rotate(brothers, num_week):
    bros1 = []
    bros2 = []

    # divide brothers into two lists
    for i in range(len(brothers)):
        if i % 2 == 0:
            bros1.append(brothers[i])
        else:
            bros2.append(brothers[i])

    for i in range(num_week):  # rotate based on which week it is

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

    return (bros1, bros2)


# creates pairings after round robin rotation
def rr_pairs(bros1, bros2):

    pairs = list(zip(bros1, bros2))  # pair up brothers

    # duplicate pairings so list stores [A,B] and [B,A] pairings
    dup = []
    for p in pairs:
        dup.append((p[1], p[0]))  # duplicate in reverse

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


def update_contacts(new_pairs, week, service):

    contact_range = cell_range('Form Responses', 'A2', 'C')
    contact_info = read_spreadsheet(service, contact_range)
    info = {}

    # get contact info
    for c in contact_info:
        info[c[1]] = [c[1], c[2]]  # name + phone number

    current_range = cell_range('This_Week', 'A1', 'C')
    updated_contact = []
    for p in new_pairs:
        updated_contact.append([p[0]] + info[p[1]])

    header = ['Week of', week, 'Phone #']
    update_spreadsheet([header] + updated_contact, service, current_range)


# syntax for reading google sheets
def cell_range(sheet, start, end):
    return sheet + "!" + start + ":" + end


if __name__ == '__main__':
    offset = 0  # rotation offsets
    if (len(sys.argv) == 2):
        offset = sys.argv[1]
    main(offset)