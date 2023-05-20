import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import httpx
import time

app = FastAPI()

# Replace the following URL with the actual URL of your React app running in Replit
origins = [
  'https://react-frontend.zeroknowledge.repl.co',
]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=['*'],
  allow_headers=['*'],
)

# API_KEY = os.environ['collegescore_api']
API_KEY = 'U4bO7BxdsEGtnGXex6TEeLwlV6gIC3dy8VP3U8nl'
COLLEGE_SCORECARD_BASE_URL = 'https://api.data.gov/ed/collegescorecard/v1/schools?'


@app.get('/')
def read_root():
  return {'Hello': 'World'}


async def fetch_colleges(state: str, page: int = 0, per_page: int = 100):
  params = {
    'api_key': API_KEY,
    'latest.school.state': state,
    'per_page': per_page,
    'page': page,
  }
  async with httpx.AsyncClient() as client:
    response = await client.get(COLLEGE_SCORECARD_BASE_URL, params=params)
    print(response)

  if response.status_code == 200:
    return response.json()
  else:
    raise Exception(f'Error: {response.status_code}')


@app.get('/colleges/{state}')
async def get_colleges(state: str):
  try:
    page = 0
    per_page = 50
    colleges = []
    while True:
      data = await fetch_colleges(state, page, per_page)
      if not data['results']:
        break
      total_list = int(data['metadata']['total'])
      for college in data['results']:

        school = {
          'Name':
          college['latest']['school']['name'],
          'Acceptance Rate':
          college['latest']['admissions']['admission_rate']['overall'],
          'Test Policy':
          college['latest']['admissions']['test_requirements'],
          'Tuition': {
            'Book Supply': college['latest']['cost']['booksupply'],
            'In State': college['latest']['cost']['tuition']['in_state'],
            'Out of State':
            college['latest']['cost']['tuition']['out_of_state'],
            'Room & Board': {
              'On Campus': college['latest']['cost']['roomboard']['oncampus'],
              'Off Campus': college['latest']['cost']['roomboard']['offcampus']
            },
          },
          'Financial Aid': {
            'Percent of Full-time, First-time Undergraduates Receiving Federal Loans':
            college['latest']['aid']['federal_loan_rate'],
            'Percentage of Full-time, First-time Pell Students':
            college['latest']['aid']['pell_grant_rate'],
            'Median Student Debt': {
              'students with family income between $0-$30,000':
              college['latest']['aid']['median_debt']['income']['0_30000'],
              'students with family income between $30,001-$75,000':
              college['latest']['aid']['median_debt']['income']['30001_75000'],
              'students with family income $75,001+':
              college['latest']['aid']['median_debt']['income']
              ['greater_than_75000'],
              'first-generation students':
              college['latest']['aid']['median_debt']
              ['first_generation_students'],
              'Percent of students who received a federal loan while in school':
              college['latest']['aid']['students_with_any_loan']
            },
          },
          'Test Scores': {
            'ACT Scores': college['latest']['admissions']['act_scores'],
            'SAT Scores': college['latest']['admissions']['sat_scores']
          },
        }

        print(school)
        colleges.append(school)
        print(f'### Page: {page} ###')
      if page < (total_list // per_page + 1):
        page += 1
        time.sleep(.25)

    return {'colleges': colleges}
  except Exception as e:
    return {'error': str(e)}


#https://api.data.gov/ed/collegescorecard/v1/schools?api_key=U4bO7BxdsEGtnGXex6TEeLwlV6gIC3dy8VP3U8nl&latest.school.state=NY&per_page=100

#results['latest']['school']['school_url']
#Acceptance Rate: 15%
#['admissions'][admission_rate]
#overall
#by_ope_id
#consumer_rate

#Test Policy: Optional
#['admissions']['test_requirements']
#Tuition: $61,450
#Room & Board: $15,033
#Financial Need Met: 100%
#Scholarship Offered

#Regular Decision Deadline: Scrape website
#Quantity of supplements: Scrape website

# uvicorn main:app --host 0.0.0.0 --port 8080
