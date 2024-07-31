from hubspot import HubSpot
from hubspot.crm.deals import SimplePublicObjectInputForCreate, SimplePublicObjectInput
# Uncomment this line and add access to token to connect to private app
#api_client = HubSpot(access_token='')

def get_all_deals(limit=100):
    try:
        api_response = api_client.crm.deals.basic_api.get_page(limit=limit, archived=False)
        deals = api_response.results
        return deals
    except Exception as e:
        print(f"An error occurred while fetching deals: {e}")
        return None

def create_new_deal(properties):
    try:
        script_deal = SimplePublicObjectInputForCreate(properties=properties)
        api_response = api_client.crm.deals.basic_api.create(simple_public_object_input_for_create=script_deal)
        return api_response
    except Exception as e:
        print(f"An error occurred while creating a new deal: {e}")
        return None

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
        
        if api_response.results:
            return api_response.results[0]
        else:
            return None
    except Exception as e:
        print(f"Exception when searching for deal: {e}")
        return None

def update_deal(deal_id, new_amount):
    try:
        properties = {
            "amount": str(new_amount)
        }
        simple_public_object_input = SimplePublicObjectInput(properties=properties)
        api_response = api_client.crm.deals.basic_api.update(deal_id=deal_id, simple_public_object_input=simple_public_object_input)
        return api_response
    except Exception as e:
        print(f"Exception when updating deal: {e}")
        return None

def print_deals(deals):
    if deals:
        print(f"Total deals fetched: {len(deals)}")
        for deal in deals:
            print(f"Deal ID: {deal.id}")
            print("Properties:")
            print(deal)
            print("-" * 50)
    else:
        print("No deals to display.")

def main():
    all_deals = get_all_deals()
    print_deals(all_deals)


    new_deal_properties = {
        "amount": "2000",
        "closedate": "2024-09-30",
        "dealname": "Script-deal",
        "dealstage": "contractsent"
    }
    new_deal = create_new_deal(new_deal_properties)
    if new_deal:
        print("New deal created:")
        print(new_deal)

    deal = find_deal_by_name("Test-Deal")

    updated_deal = update_deal(deal.id, 7777)
    if updated_deal:
        print(f"Deal 'Test-Deal' updated successfully. New amount: 7777")
    else:
        print("Failed to update the deal.")

if __name__ == "__main__":
    main()