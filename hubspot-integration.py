from hubspot import HubSpot
from hubspot.crm.deals import SimplePublicObjectInput, SimplePublicObjectInputForCreate
import os
from datetime import datetime, timezone

# Initialize HubSpot client
# api_client = HubSpot(access_token='')

# This function retrieves up to 100 deals present in HubSpot
def get_all_deals(limit=100):
    try:
        api_response = api_client.crm.deals.basic_api.get_page(limit=limit, archived=False)
        return api_response.results
    except Exception as e:
        print(f"An error occurred while fetching deals: {e}")
        return None

# This function creates a new deal
def create_new_deal(properties):
    properties.pop("last_updated", None)
    try:
        script_deal = SimplePublicObjectInputForCreate(properties=properties)
        return api_client.crm.deals.basic_api.create(simple_public_object_input_for_create=script_deal)
    except Exception as e:
        print(f"An error occurred while creating a new deal: {e}")
        return None

# This function does a look up of deals by name
def find_deal_by_name(deal_name):
    try:
        filter = {"propertyName": "dealname", "operator": "EQ", "value": deal_name}
        sort = [{"propertyName": "createdate", "direction": "DESCENDING"}]
        properties = ["dealname", "amount", "hs_lastmodifieddate"]
        public_object_search_request = {
            "filters": [filter],
            "sorts": sort,
            "properties": properties
        }
        api_response = api_client.crm.deals.search_api.do_search(public_object_search_request=public_object_search_request)
        
        return api_response.results[0] if api_response.results else None
    except Exception as e:
        print(f"Exception when searching for deal: {e}")
        return None

# This function updates a deal if their last update time is outdated.
    
def update_deal(deal, new_properties):
    try:
        last_updated_str = new_properties.get("last_updated")
        if last_updated_str:
            try:
                last_updated = datetime.strptime(last_updated_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                print(f"Invalid date format for last_updated: {last_updated_str}. Expected format: YYYY-MM-DD")
                return None

        hs_lastmodified_str = deal.properties.get('hs_lastmodifieddate')
        if hs_lastmodified_str:
            hs_lastmodified = datetime.strptime(hs_lastmodified_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
        else:
            print("hs_lastmodifieddate not found in deal properties")
            return None

        if last_updated > hs_lastmodified:
            new_properties.pop("last_updated", None)
            simple_public_object_input = SimplePublicObjectInput(properties=new_properties)
            return api_client.crm.deals.basic_api.update(deal_id=deal.id, simple_public_object_input=simple_public_object_input)
        else:
            print("Deal already contains latest information")
            return None
    except Exception as e:
        print(f"Exception when updating deal: {e}")
        return None

def print_deals(deals):
    if deals:
        print(f"Total deals fetched: {len(deals)}")
        for deal in deals:
            print(f"Deal ID: {deal.id}")
            print("Properties:")
            print(deal.properties)
            print("-" * 50)
    else:
        print("No deals to display.")


def main():
    try:
        all_deals = get_all_deals()
        print_deals(all_deals)

        new_deal_properties = {
            "amount": "3000",
            "closedate": "2024-09-30",
            "dealname": "Script-deal2",
            "dealstage": "contractsent",
            "last_updated": "2024-8-1"
        }
        
        existing_deal = find_deal_by_name(new_deal_properties.get("dealname"))
        
        if existing_deal is None:
            new_deal = create_new_deal(new_deal_properties)
            if new_deal:
                print("New deal created:")
                print(new_deal.properties)
        else:
            updated_deal = update_deal(existing_deal, new_deal_properties)
            if updated_deal:
                print("Deal updated:")
                print(updated_deal.properties)

        test_deal = find_deal_by_name("Test-Deal")
        
        if test_deal:
            updated_properties = {
                "amount": "7777",
                "last_updated": "2024-07-31"
            }
            updated_deal = update_deal(test_deal, updated_properties)
            if updated_deal:
                print(f"Deal 'Test-Deal' updated successfully. New amount: 7777")
            else:
                print("No update was necessary.")
        else:
            print("Deal 'Test-Deal' not found.")
    except Exception as e:
        print(f"An error occurred in the main function: {e}")

if __name__ == "__main__":
    main()