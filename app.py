import requests
import random
import json
import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

def duplicate_and_modify_dashboard_tab_questions(api_key, base_url, dashboard_id, tab_name, modification_function):
  """
  This function retrieves questions from a Metabase dashboard tab, duplicates them 
  with modifications, and uploads them to a new tab.

  Args:
      api_key (str): Your Metabase API key.
      base_url (str): The base URL of your Metabase instance.
      dashboard_id (int): The ID of the dashboard containing the tab.
      tab_name (str): The name of the tab with the questions to duplicate.
      modification_function (function): A function that takes a question dictionary 
                                         and returns a modified dictionary.
  """

  # Get dashboard details
  dashboard_url = f"{base_url}/api/dashboard/{dashboard_id}"
  headers = {"x-api-key": api_key}
  response = requests.get(dashboard_url, headers=headers)
  dashboard_data = response.json()

  # Save the tabs config
  tabs = dashboard_data["tabs"]

  # Find the target tab
  target_tab_id = None
  for tab in tabs:
    if tab["name"] in tab_name:
      target_tab_id = tab["id"]
      break

  if not target_tab_id:
    raise Exception(f"Tab '{tab_name}' not found in dashboard {dashboard_id}")

  # Duplicate and modify all questions of the tab
  new_dashcards = []
  new_tab_id = random.randrange(200, 5000, 3)
  for dashcard in dashboard_data['dashcards']:
    if dashcard['dashboard_tab_id'] == target_tab_id:
      # Duplicate each question
      response = requests.post(f"{base_url}/api/card/{dashcard['card_id']}/copy", headers=headers)
      duplicated_dashcard = response.json()
      
      # Modify the card config
      new_dashcard = dashcard.copy()
      new_dashcard['id'] = random.randrange(2000, 50000, 3)
      if 'id' in duplicated_dashcard.keys():  # otherwise it's a card text
        new_dashcard['card_id'] = duplicated_dashcard['id']
      
        new_dashcard['dashboard_tab_id'] = new_tab_id
        modified_dashcard = modification_function(new_dashcard)

        updated_data = {
          'name': modified_dashcard["card"]["name"].replace('Viande/Volaille 🥩', 'Poisson 🐟'),
          'dataset_query': json.loads(json.dumps(modified_dashcard["card"]["dataset_query"]).replace('meat_poultry', 'fish'))
        }
        response = requests.put(f"{base_url}/api/card/{modified_dashcard['card_id']}", headers=headers, json=updated_data)
        duplicated_dashcard = response.json()

        new_dashcards.append(modified_dashcard)

  
  # Update the tab config
  dashboard_data['dashcards'] += new_dashcards
  # Create a new tab with a unique name (e.g., "Modified - {original_tab_name}")
  new_tab_name = f"Modified - {tab_name}"

  # Upload the new questions to the new tab
  create_tab_url = f"{base_url}/api/dashboard/{dashboard_id}"
  tabs.append(
    {
      'id': new_tab_id,
      'name': new_tab_name
    }
  )
  response = requests.put(create_tab_url, headers=headers, json=dashboard_data)

  if response.status_code == 200:
    print(f"Successfully duplicated and modified questions from tab ")
  else: 
    print("Error")

# Example usage
def modify_question_name(question):
  if 'name' in question['card'].keys():
    try:
      question["card"]["name"] = question["card"]["name"].replace('Viande/Volaille 🥩', 'Poisson 🐟')
    except Exception as e:
      print(e)
    return question


api_key = os.getenv('API_KEY')
base_url = os.getenv('BASE_URL')
dashboard_id = os.getenv('DASHBOARD_ID')
tab_name = os.getenv('TAB_NAME')
duplicate_and_modify_dashboard_tab_questions(api_key, base_url, dashboard_id, tab_name, modify_question_name)