# hubspot-integration

Run `pip install -r requirements.txt` for installing all dependencies.. 

## How to run after installing all tools:
HUBSPOT_API_KEY=API_KEY uvicorn fast-api-hubspot:app --reload
## Get Deal
curl -X GET "http://localhost:8000/deals/Test-Deal"

## Check if deal already exists
curl -X POST "http://localhost:8000/create-deal" \
-H "Content-Type: application/json" \
-d '{
  "amount": 3000,
  "closedate": "2024-10-30",
  "dealname": "fast-api-deal",
  "dealstage": "contractsent",
  "last_updated": "2024-08-07"
}'

## Create new deal
curl -X POST "http://localhost:8000/create-deal" \
-H "Content-Type: application/json" \
-d '{
  "amount": 3000,
  "closedate": "2024-10-30",
  "dealname": "fast-api-deal",
  "dealstage": "contractsent",
  "last_updated": "2024-08-07"
}'

## Update a deal
curl -X PUT "http://localhost:8000/update-deal" \
-H "Content-Type: application/json" \
-d '{
  "name": "Test-Deal",
  "amount": 10000,
  "last_updated": "2024-08-07"
}'

## Update a deal that already has the latest info
curl -X PUT "http://localhost:8000/update-deal" \
-H "Content-Type: application/json" \
-d '{
  "name": "Test-Deal",
  "amount": 10000,
  "last_updated": "2024-08-07"}'