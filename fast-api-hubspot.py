from fastapi import FastAPI, HTTPException
from hubspot import HubSpot
from hubspot.crm.deals import SimplePublicObjectInput, SimplePublicObjectInputForCreate
from pydantic import BaseModel
import os
from datetime import datetime, date

app = FastAPI()

# Initialize HubSpot client
# api_client = HubSpot(access_token='')

class DealCreate(BaseModel):
    amount: float
    closedate: date
    dealname: str
    dealstage: str
    last_updated: date

class DealUpdate(BaseModel):
    id: str
    amount: float
    last_updated: date

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
            raise HTTPException(status_code=404, detail="Deal not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.post("/deals")
def create_new_deal(deal: DealCreate):
    properties = deal.dict()
    properties.pop("last_updated", None)
    try:
        script_deal = SimplePublicObjectInputForCreate(properties=properties)
        response = api_client.crm.deals.basic_api.create(simple_public_object_input_for_create=script_deal)
        return response.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while creating a new deal: {str(e)}")

@app.put("/deals")
def update_deal(deal: DealUpdate):
    try:
        existing_deal = api_client.crm.deals.basic_api.get_by_id(deal_id=deal.id)
        hs_lastmodified = datetime.fromisoformat(existing_deal.properties['hs_lastmodifieddate'].replace('Z', '+00:00'))
        last_updated = deal.last_updated.replace(tzinfo=hs_lastmodified.tzinfo)

        if last_updated > hs_lastmodified:
            properties = {"amount": str(deal.amount)}
            simple_public_object_input = SimplePublicObjectInput(properties=properties)
            response = api_client.crm.deals.basic_api.update(deal_id=deal.id, simple_public_object_input=simple_public_object_input)
            return response.to_dict()
        else:
            return {"message": "Deal already contains latest information"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while updating the deal: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)