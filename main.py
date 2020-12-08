from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import random
import copy

# If modifying these scopes, delete the file token.pickle.

#read/write
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.

#fa20bros spreadsheet
SAMPLE_SPREADSHEET_ID = '1NvMdLi3mPeO8WWEH0cC_yMCakPRq8IYq67X-0Fb4iJU'
SAMPLE_RANGE_NAME = 'api_testing!A2:L'

def main():
    values, service = read_spreadsheet()

    brothers = []

    pair_dict = {}

    for v in values:

        #get list of brothers
        brothers.append(v[0])

        #read in past pairings into dictionary for each brother
        pair_dict[v[0]] = []

        #brothers paired with before
        pair_list = v[1:]

        #account for possibility of group of 3 brothers
        for pair in pair_list:
            pairings = pair.split(',')
            for p in pairings:
                pair_dict[v[0]].append(p.strip())

    print(len(brothers))

    #at this point we have brothers (list of bros) and
    #pair_dict (dictionary for each brother and all brothers prev paired with)

    new_pairings = {}
    paired_bros = []

    for v in values:

        if v[0] in paired_bros:     #pairing made earlier
            v.append(new_pairings[v[0]])

        else:
            bros = copy.deepcopy(brothers)         #copy list of brothers remaining

            bros.remove(v[0])
            for p in pair_dict[v[0]]:   #remove brothers already paired before
                if p in bros:
                    bros.remove(p)

            if (len(bros) == 2):        #if only 3 bros total left
                v.append(bros[0] + ", " + bros[1])
                new_pairings[bros[0]] = bros[1] + ", " + v[0]
                new_pairings[bros[1]] = v[0] + ", " + bros[0]

                paired_bros.append(bros[0])
                paired_bros.append(bros[1])

                brothers.remove(bros[0])    #remove all brothers from remaining list
                brothers.remove(bros[1])
                brothers.remove(v[0])

            else:
                new_bro = random.choice(bros)   #pick random brother from remaining
                new_pairings[new_bro] = v[0]    #add new pairing
                v.append(new_bro)

                paired_bros.append(new_bro)

                brothers.remove(new_bro)
                brothers.remove(v[0])


    update_spreadsheet(values, service)


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