import os
from fastapi import FastAPI, HTTPException
from hubspot import HubSpot
from hubspot.crm.deals import SimplePublicObjectInput, SimplePublicObjectInputForCreate
from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional
from dateutil import parser
from pytz import UTC

app = FastAPI()

# Load API key from environment variable
api_key = os.getenv('HUBSPOT_API_KEY')
if not api_key:
    raise ValueError("HUBSPOT_API_KEY environment variable is not set")

# Initialize HubSpot client
api_client = HubSpot(access_token=api_key)

class DealCreate(BaseModel):
    amount: float
    closedate: date
    dealname: str
    dealstage: str
    last_updated: date

class DealUpdate(BaseModel):
    name: str
    amount: float
    last_updated: date

# Send a get request to this url
@app.get("/deals/{deal_name}")
def find_deal_by_name(deal_name: str):
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
            return api_response.results[0].to_dict()
        else:
            return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# Create deals by sending new deal properties to this url
@app.post("/create-deal")
def create_new_deal(deal: DealCreate):
    try:
        existing_deal = find_deal_by_name(deal.dealname)
        if existing_deal:
            raise HTTPException(status_code=400, detail="Deal already exists")
    except HTTPException as e:
        if e.status_code != 404:
            raise e

    properties = deal.dict()
    properties.pop("last_updated", None)
    try:
        script_deal = SimplePublicObjectInputForCreate(properties=properties)
        response = api_client.crm.deals.basic_api.create(simple_public_object_input_for_create=script_deal)
        return response.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while creating a new deal: {str(e)}")

# Update deals by sending latest property values to this url
@app.put("/update-deal")
def update_deal(deal: DealUpdate):
    try:
        existing_deal = find_deal_by_name(deal.name)
        if existing_deal is None:
            raise HTTPException(status_code=404, detail="Deal not found")

        hs_lastmodified_str = existing_deal['properties'].get('hs_lastmodifieddate')
        if not hs_lastmodified_str:
            raise HTTPException(status_code=500, detail="hs_lastmodifieddate not found in deal properties")

        hs_lastmodified = parser.isoparse(hs_lastmodified_str).replace(tzinfo=UTC)
        last_updated = datetime.combine(deal.last_updated, datetime.min.time()).replace(tzinfo=UTC)

        if last_updated > hs_lastmodified:
            properties = {"amount": str(deal.amount)}
            simple_public_object_input = SimplePublicObjectInput(properties=properties)
            response = api_client.crm.deals.basic_api.update(deal_id=existing_deal['id'], simple_public_object_input=simple_public_object_input)
            return response.to_dict()
        else:
            return {"message": "Deal already contains the latest information"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while updating the deal: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)