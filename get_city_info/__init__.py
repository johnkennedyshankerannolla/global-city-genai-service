import azure.functions as func
import logging
import json
from .helper import fetch_city_data

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing city info request.')

    city = req.params.get('city')
    if not city:
        try:
            req_body = req.get_json()
        except ValueError:
            return func.HttpResponse("Invalid JSON body", status_code=400)
        else:
            city = req_body.get('city')

    if not city:
        return func.HttpResponse("City name required", status_code=400)

    try:
        result = fetch_city_data(city)
        return func.HttpResponse(json.dumps(result), mimetype="application/json")
    except Exception as e:
        logging.error(f"Error fetching city info: {e}")
        return func.HttpResponse("Internal Server Error", status_code=500)
