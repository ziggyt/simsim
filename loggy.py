import logging
from beamngpy import BeamNGpy
from beamngpy.sensors import RoadsSensor
import time
import csv

def main():
    # Set up logging
    logging.basicConfig(level=logging.DEBUG)

    try:
        # Connect to the existing BeamNG.tech instance
        bng = BeamNGpy('localhost', 64256)
        bng.open(launch=False)
        
        logging.info("Connected to existing BeamNG.tech instance")

        # Wait for the scenario to start
        scenario_started = False
        while not scenario_started:
            try:
                gamestate = bng.get_gamestate()
                if gamestate['state'] == 'scenario' and gamestate['scenario_state'] == 'running':
                    logging.info("Scenario is running. Starting to log road distances.")
                    scenario_started = True
                else:
                    time.sleep(1)  # Check every second
            except Exception as e:
                logging.warning(f"Error checking game state: {e}")
                time.sleep(1)  # Wait a bit before retrying

        # Get the current scenario
        scenario = bng.scenario.get_current()

        # Get the player vehicle
        player_vehicle = scenario.get_vehicle('ego_vehicle')

        # Create RoadsSensor
        roads_sensor = RoadsSensor('roads', bng, player_vehicle)

        # Open CSV file for logging
        with open('road_distances.csv', 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['Timestamp', 'DistanceToLeft', 'DistanceToRight'])

            start_time = time.time()
            while True:
                # Update scenario
                scenario.update()

                # Get road data
                road_data = roads_sensor.poll()
                logging.debug(f"Road data: {road_data}")

                # Log road distances
                timestamp = time.time() - start_time
                if isinstance(road_data, dict) and 'dist2Left' in road_data and 'dist2Right' in road_data:
                    csv_writer.writerow([timestamp, road_data['dist2Left'], road_data['dist2Right']])
                elif isinstance(road_data, list) and len(road_data) >= 2:
                    csv_writer.writerow([timestamp, road_data[0], road_data[1]])
                else:
                    logging.warning(f"Unexpected road data format: {road_data}")
                    csv_writer.writerow([timestamp, 'N/A', 'N/A'])

                time.sleep(0.1)

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)
    finally:
        # Close the connection
        if 'bng' in locals():
            bng.close()

if __name__ == "__main__":
    main()
