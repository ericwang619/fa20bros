from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.

#read/write
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.

#fa20bros spreadsheet
SAMPLE_SPREADSHEET_ID = '1NvMdLi3mPeO8WWEH0cC_yMCakPRq8IYq67X-0Fb4iJU'
SAMPLE_RANGE_NAME = 'api_testing!D:E'

def main():

    service = credentials()

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()

    #get values from range above, ignores rows with no data
    values = result.get('values', [])

    #matrix (list of lists) for values to be added
    new_values = []
    if not values:
        print('No data found.')

    for row in values:
        print(row)
        new_values.append(["1", "test"])

    update_spreadsheet(new_values, service)


def update_spreadsheet(new_values, service):
    body = {
        'values': new_values
    }
    result = service.spreadsheets().values().update(
        spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME,
        valueInputOption='USER_ENTERED', body=body).execute()
    print('{0} cells updated.'.format(result.get('updatedCells')))


def credentials():
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
    return service


if __name__ == '__main__':
    main()