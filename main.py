from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from collections import deque

# If modifying these scopes, delete the file token.pickle.

# read/write
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.

# fa20bros spreadsheet
SAMPLE_SPREADSHEET_ID = '1NvMdLi3mPeO8WWEH0cC_yMCakPRq8IYq67X-0Fb4iJU'
SAMPLE_RANGE_NAME = 'api_testing!A2:AZ'


def main():
    new_pairing()


def new_pairing():
    values, service = read_spreadsheet()  # read in spreadsheet

    brothers = []
    num_week = len(values[0]) - 2

    for v in values:
        brothers.append(v[1])  # get all brothers (hidden column that stores initial pairings)

    brothers = rr_rotate(brothers, num_week)  # do round robin rotation

    pairs = rr_pairs(brothers)  # pair up brothers

    for i in range(len(pairs)):  # add new column for new pairings
        values[i].append(pairs[i][1])

    update_spreadsheet(values, service)


# performs round robin rotation on brothers. Number of rotations depends on the week
# round robin rotation fixes first brother, rotates all others
# example with 4 bros: (1, 2), (3, 4) -> (1, 3), (4, 2) -> (1, 4), (2, 3)
def rr_rotate(brothers, num_week):

    for i in range(num_week):       # rotate based on which week it is

        mid = int(len(brothers) / 2)    # split into two halves
        bros1 = brothers[:mid]
        bros2 = brothers[mid:]

        first_bro_1 = bros1[0]      # store edge bros
        last_bro_2 = bros2[-1]

        bros1 = deque(bros1)        # deque for rotation
        bros2 = deque(bros2)

        bros1.rotate(-1)
        bros2.rotate(1)

        bros1 = list(bros1)
        bros2 = list(bros2)

        bros1[-1] = last_bro_2      # update edge bros
        bros2[0] = bros1[0]
        bros1[0] = first_bro_1

        brothers = bros1 + bros2    # combine halves

    return brothers


# creates pairings after round robin rotation
def rr_pairs(brothers):
    mid = int(len(brothers) / 2)  # split up brothers into two halves
    bros1 = brothers[:mid]
    bros2 = brothers[mid:]

    pairs = list(zip(bros1, bros2))  # pair up brothers

    dup = []
    for p in pairs:
        dup.append((p[1], p[0]))  # duplicate in reverse

    pairs = pairs + dup
    pairs.sort()  # sort alphabetically

    return pairs


def read_spreadsheet():
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
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    # get values from range above, ignores rows with no data
    values = result.get('values', [])
    return values, service


def update_spreadsheet(new_values, service):
    body = {
        'values': new_values
    }
    result = service.spreadsheets().values().update(
        spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME,
        valueInputOption='USER_ENTERED', body=body).execute()
    print('{0} cells updated.'.format(result.get('updatedCells')))


if __name__ == '__main__':
    main()
