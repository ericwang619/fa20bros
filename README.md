# term_pairs

Tool for randomizing weekly prayer pairings using Google Spreadsheet API 

Setting up:
1. On web browser:\
    a. Create a Google form for participants to sign up on. \
       &nbsp;&nbsp;&nbsp;&nbsp;Must have "Name" and "Phone #" as first and second question respectively.\
    b. From the Google form's responses tab, create a Google spreadsheet to view responses \
    c. In the Google spreadsheet, rename the responses sheet to "Form Responses" \
    d. Add a new sheet called "This_Week" \
    e. Add another new sheet called "All_Pairs", then type "Week of" in cell A1.  
       &nbsp;&nbsp;&nbsp;&nbsp;In the rest of row 1 beginning with column B, add the dates for the weeks you'll be using for the rotations 
2. Collect Google form responses (code will not work w/o responses) 
3. Using the tool: \
    a. download code from git repo \
    b. In terminal or IDE, Open main.py and update spreadsheet ID  
       &nbsp;&nbsp;&nbsp;&nbsp;(url for Google spreadsheet is docs.google.com/spreadsheets/d/<SPREADSHEET_ID/) \
    c. Run one of the following files (will need to sign in with a google account during execution): \
    &nbsp;&nbsp;&nbsp;&nbsp;i. main.py - creates the rotation for the next week \
       &nbsp;&nbsp;&nbsp;ii. make_pairs.py - runs main.py and then tests for duplicates \
      &nbsp;&nbsp;iii. multiple_pairs.py - create multiple rotations (change iter to set the number of rotations, default = 5) \
    d. Repeat 3.c to create additional rotations 
   
Note: to create new rotations for a different spreadsheet, modify SPREADSHEET_ID and delete token.pickle


File descriptions: \
main.py - contains the code for the pairing algorithm \
test.py - checks for duplicate pairs \
make_pairs.py - runs main.py once and then the test \
multiple_pairs.py - runs main.py multiple times

Notable variables: \
offset - adds to the number of rotations done \
   &nbsp;&nbsp;&nbsp;&nbsp; - can pass in using main(offset) or python multiple_pairs.py offset
    
