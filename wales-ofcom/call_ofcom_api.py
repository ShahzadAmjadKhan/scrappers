#!/usr/bin/env python3
import requests
import csv
import json
import time
import os
import sys
import argparse

# Create output directory
os.makedirs('ofcom/output/api_responses', exist_ok=True)

# API configuration
API_BASE_URL = "https://api-proxy.ofcom.org.uk/broadband"
API_ENDPOINT = "/coverage/{PostCode}"

# Function to call the Ofcom API for a postcode
def get_broadband_data(postcode, api_key):
    if not api_key:
        print("Error: API key not provided.")
        sys.exit(1)
        
    # Remove spaces from postcode to match API requirements
    formatted_postcode = postcode.replace(" ", "")
    
    url = f"{API_BASE_URL}{API_ENDPOINT}".replace("{PostCode}", formatted_postcode)
    
    headers = {
        "Ocp-Apim-Subscription-Key": api_key
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        # Check if the request was successful
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            print(f"Postcode not found: {postcode}")
            return {"error": "not_found", "status_code": 404}
        else:
            print(f"API error for postcode {postcode}: Status code {response.status_code}")
            return {"error": "api_error", "status_code": response.status_code}
            
    except Exception as e:
        print(f"Error making API request for postcode {postcode}: {str(e)}")
        return {"error": "request_failed", "error_message": str(e)}

# Main function
def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Call Ofcom API for postcodes')
    parser.add_argument('--api-key', required=True, help='Ofcom API subscription key')
    parser.add_argument('--input', default='ofcom/output/wales_postcodes.csv', help='Input CSV file with postcodes')
    parser.add_argument('--output', default='ofcom/output/broadband_data.csv', help='Output CSV file for results')
    parser.add_argument('--limit', type=int, help='Limit number of postcodes to process')
    
    args = parser.parse_args()
    
    input_file = args.input
    output_file = args.output
    api_key = args.api_key
    
    # Read postcodes from input CSV
    postcodes = []
    try:
        with open(input_file, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip header row
            for row in reader:
                if len(row) > 1 and row[1].strip():  # Ensure postcode exists
                    postcodes.append(row[1])
    except Exception as e:
        print(f"Error reading input file: {str(e)}")
        return
    
    # Apply limit if specified
    if args.limit and args.limit > 0:
        postcodes = postcodes[:args.limit]
        print(f"Limited to first {args.limit} postcodes")
    
    print(f"Found {len(postcodes)} postcodes to process")
    
    # Create output CSV file with headers
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = [
            'PostCode', 
            'Status', 
            'AddressCount',
            'MaxDownSpeed',
            'MaxUpSpeed',
            'ResponseFile'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Process each postcode
        for i, postcode in enumerate(postcodes):
            print(f"Processing {i+1}/{len(postcodes)}: {postcode}")
            
            # Call API
            response_data = get_broadband_data(postcode, api_key)
            
            # Prepare data for CSV
            row_data = {
                'PostCode': postcode,
                'Status': 'success' if 'error' not in response_data else response_data['error'],
                'AddressCount': len(response_data.get('Availability', [])) if 'Availability' in response_data else 0,
                'MaxDownSpeed': 'N/A',
                'MaxUpSpeed': 'N/A',
                'ResponseFile': ''
            }
            
            # If successful, extract more information
            if 'error' not in response_data and 'Availability' in response_data:
                # Find max speeds across all addresses
                max_down = -1
                max_up = -1
                
                for address in response_data['Availability']:
                    if 'MaxPredictedDown' in address and address['MaxPredictedDown'] > max_down:
                        max_down = address['MaxPredictedDown']
                    if 'MaxPredictedUp' in address and address['MaxPredictedUp'] > max_up:
                        max_up = address['MaxPredictedUp']
                
                row_data['MaxDownSpeed'] = max_down if max_down >= 0 else 'N/A'
                row_data['MaxUpSpeed'] = max_up if max_up >= 0 else 'N/A'
                
                # Save full response to JSON file
                response_filename = f"postcode_{postcode.replace(' ', '_')}.json"
                response_filepath = os.path.join('ofcom/output/api_responses', response_filename)
                
                with open(response_filepath, 'w') as jsonfile:
                    json.dump(response_data, jsonfile, indent=2)
                
                row_data['ResponseFile'] = response_filename
            
            # Write to CSV
            writer.writerow(row_data)
            
            # Be nice to the API - add a small delay between requests
            time.sleep(0.5)
    
    print(f"Processing completed. Results saved to {output_file}")

if __name__ == "__main__":
    main() 