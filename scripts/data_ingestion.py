import requests
import pandas as pd
from datetime import datetime, timedelta
import json
import time
from datetime import datetime, timedelta

def get_airport_flight_data(airport_code, flight_type='arrivals'):
    """Get detailed flight data for a specific airport"""

    url = (
        f"https://api.flightradar24.com/common/v1/airport.json?"
        f"code={airport_code}&plugin[]=schedule"
        f"&plugin-setting[schedule][mode]={flight_type}"
    )
    
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'Origin': 'https://www.flightradar24.com',
        'Referer': f'https://www.flightradar24.com/data/airports/{airport_code.lower()}/{flight_type}'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if data.get('result', {}).get('response', {}).get('airport', {}).get('pluginData', {}).get('schedule', {}).get(flight_type, {}).get('data'):
            flights = data['result']['response']['airport']['pluginData']['schedule'][flight_type]['data']
            return flights
        else:
            print(f"No {flight_type} data found for {airport_code}")
            return []
        

            
    except Exception as e:
        print(f"Error fetching {flight_type} for {airport_code}: {e}")
        return []

def extract_flight_details(flight_data, flight_type, airport_code):
    """Extract detailed information from flight data"""
    try:
        # The actual data is under the 'flight' key
        flight = flight_data.get('flight', flight_data)  # fallback to root if not present

        flight_info = {
            'flight_id': flight.get('identification', {}).get('id', 'N/A'),
            'flight_number': flight.get('identification', {}).get('number', {}).get('default', 'N/A'),
            'callsign': flight.get('identification', {}).get('callsign', 'N/A'),
            'airline': flight.get('airline', {}).get('name', 'N/A'),
            'airline_iata': flight.get('airline', {}).get('code', {}).get('iata', 'N/A'),
            'airline_icao': flight.get('airline', {}).get('code', {}).get('icao', 'N/A'),
            'aircraft_model': flight.get('aircraft', {}).get('model', {}).get('text', 'N/A'),
            'aircraft_code': flight.get('aircraft', {}).get('model', {}).get('code', 'N/A'),
            'registration': flight.get('aircraft', {}).get('registration', 'N/A'),
            'status': flight.get('status', {}).get('text', 'N/A'),
            'status_category': flight.get('status', {}).get('generic', {}).get('status', {}).get('text', 'N/A'),
        }

        # Time information
        time_data = flight.get('time', {})
        flight_info.update({
            'scheduled': time_data.get('scheduled', {}).get('arrival' if flight_type == 'arrivals' else 'departure', 'N/A'),
            'estimated': time_data.get('estimated', {}).get('arrival' if flight_type == 'arrivals' else 'departure', 'N/A'),
        })

        # Airport information
        airport_data = flight.get('airport', {})
        if flight_type == 'arrivals':
            flight_info.update({
                'origin_airport': airport_data.get('origin', {}).get('name', 'N/A'),
                'origin_iata': airport_data.get('origin', {}).get('code', {}).get('iata', 'N/A'),
                'origin_icao': airport_data.get('origin', {}).get('code', {}).get('icao', 'N/A'),
                'origin_city': airport_data.get('origin', {}).get('position', {}).get('region', {}).get('city', 'N/A'),
                'origin_country': airport_data.get('origin', {}).get('position', {}).get('country', {}).get('name', 'N/A'),
                'destination_airport': f"Mohammed V (CMN)" if airport_code == 'CMN' else f"Rabat-Salé (RBA)",
                'destination_iata': airport_code,
            })
        else:  # departures
            flight_info.update({
                'origin_airport': f"Mohammed V (CMN)" if airport_code == 'CMN' else f"Rabat-Salé (RBA)",
                'origin_iata': airport_code,
                'destination_airport': airport_data.get('destination', {}).get('name', 'N/A'),
                'destination_iata': airport_data.get('destination', {}).get('code', {}).get('iata', 'N/A'),
                'destination_icao': airport_data.get('destination', {}).get('code', {}).get('icao', 'N/A'),
                'destination_city': airport_data.get('destination', {}).get('position', {}).get('region', {}).get('city', 'N/A'),
                'destination_country': airport_data.get('destination', {}).get('position', {}).get('country', {}).get('name', 'N/A'),
            })

        # Additional info
        flight_info.update({
            'flight_type': flight_type[:-1],  # remove 's'
            'data_airport': airport_code,
            'data_timestamp': datetime.now().isoformat(),
            'baggage_claim': airport_data.get('destination', {}).get('info', {}).get('baggage', 'N/A'),
            'terminal': airport_data.get('destination' if flight_type == 'arrivals' else 'origin', {}).get('info', {}).get('terminal', 'N/A'),
            'gate': airport_data.get('destination' if flight_type == 'arrivals' else 'origin', {}).get('info', {}).get('gate', 'N/A'),
        })

        return flight_info

    except Exception as e:
        print(f"Error extracting flight details: {e}")
        return None

def extract_data_from_api(data_path):
    airports = ['CMN', 'RAK', 'AGA', 'RBA', 'TNG', 'FEZ']
    flight_types = ['arrivals', 'departures']
    
    all_flights_data = []
    
    print("Fetching current flight data...")
    
    for airport in airports:
        for flight_type in flight_types:
            print(f"Getting {flight_type} for {airport}...")
            
            flights = get_airport_flight_data(airport, flight_type)
            print(f"Found {len(flights)} {flight_type} for {airport}")
            
            for flight in flights:
                flight_details = extract_flight_details(flight, flight_type, airport)
                if flight_details:
                    all_flights_data.append(flight_details)
            
            # Be respectful to the API - add delay
            time.sleep(1)
    
    # Save to CSV
    if all_flights_data:
        df = pd.DataFrame(all_flights_data)
        filename = data_path
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Data saved to {filename}")
        # Show summary
        print("\n=== SUMMARY ===")
        print(f"Total flights collected: {len(df)}")
        print("By airport:")
        print(df['data_airport'].value_counts())
        print("By flight type:")
        print(df['flight_type'].value_counts())
        
        # Show sample
        print(f"\nSample data:")
        print(df[['flight_id', 'flight_number', 'callsign', 'airline', 'airline_iata',
       'airline_icao', 'aircraft_model', 'aircraft_code', 'registration',
       'status', 'status_category', 'scheduled', 'estimated',
       'origin_airport', 'destination_airport','flight_type', 'data_airport',
       'terminal']].head(10))

        df['delay_minutes'] = (df['estimated'] - df['scheduled']) / 60
        delayed_flights = df[df['delay_minutes'] != 0]
        print(delayed_flights[['data_airport', 'delay_minutes']].groupby('data_airport').mean())
        print(delayed_flights[['data_airport', 'delay_minutes']].describe())
        print(delayed_flights[['data_airport', 'delay_minutes']].head(10))
        
#extract_data_from_api('./data/morocco_flights.csv')