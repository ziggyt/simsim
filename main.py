import logging
from beamngpy import BeamNGpy, Scenario, Vehicle
import math
import time

def main():
    # Set up logging
    logging.basicConfig(level=logging.DEBUG)

    # Specify the path to your BeamNG.tech installation
    beamng_home = r"C:\Users\max\Documents\BeamNG.tech.v0.32.5.0\BeamNG.tech.v0.32.5.0"

    try:
        # Connect to BeamNG.tech
        bng = BeamNGpy('localhost', 64256, home=beamng_home)
        bng.open(launch=True)
        
        logging.info("Connected to BeamNG.tech")

        # Create a scenario in East Coast USA map
        scenario = Scenario('east_coast_usa', 'Intoxeye User Test v0.1')
        
        # Highway spawn point coordinates for player
        player_spawn = (903.470642, -235.299133, 40.2094994)
        
        # Player rotation (45 degrees to the left)
        player_rot_quat = (0, 0, 0.3826834, 0.9238795)  # This is a 45-degree rotation around the Z-axis
        
        # NPC spawn coordinates
        npc_spawn = (909.38092, -272.285278, 40.5305939)
        
        # NPC rotation
        npc_rot_quat = (0, 0, -0.042764, 0.999085)
        
        # Create and add the player's vehicle
        player_vehicle = Vehicle('ego_vehicle', model='etk800', license='RISE')
        scenario.add_vehicle(player_vehicle, pos=player_spawn, rot_quat=player_rot_quat)

        # Create and add the NPC vehicle
        npc_vehicle = Vehicle('npc', model='etk800', license='MR RECKLESS')
        scenario.add_vehicle(npc_vehicle, pos=npc_spawn, rot_quat=npc_rot_quat)

        logging.info("Vehicles added to scenario")

        # Load the scenario
        scenario.make(bng)
        logging.info("Scenario created")

        # Load the scenario in BeamNG.tech
        bng.load_scenario(scenario)
        logging.info("Scenario loaded in BeamNG.tech")

        # Set up initial state
        player_vehicle.ai.set_mode('manual')
        npc_vehicle.ai.set_mode('disabled')
        logging.info("Vehicle AI modes set")

        logging.info("Waiting for the user to start the scenario in BeamNG.tech...")

        # Wait for the scenario to start
        scenario_started = False
        while not scenario_started:
            try:
                gamestate = bng.get_gamestate()
                if gamestate['state'] == 'scenario' and gamestate['scenario_state'] == 'running':
                    logging.info("Scenario started by user.")
                    scenario_started = True
                else:
                    time.sleep(1)  # Check every second
            except Exception as e:
                logging.warning(f"Error checking game state: {e}")
                time.sleep(1)  # Wait a bit before retrying

        npc_triggered = False

        while True:
            # Update vehicle states
            scenario.update()

            # Get player position
            player_pos = player_vehicle.state['pos']

            # Get NPC position
            npc_pos = npc_vehicle.state['pos']

            # Calculate distance between player and NPC
            distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(player_pos, npc_pos)))

            # If player is closer than 20 meters and NPC hasn't been triggered yet, make NPC drive
            if distance < 20 and not npc_triggered:
                npc_vehicle.ai.set_mode('span')
                npc_vehicle.ai.drive_in_lane(True)
                npc_triggered = True
                logging.info("NPC has been triggered and is now driving!")

            time.sleep(0.1)

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)
    finally:
        # Close the connection
        if 'bng' in locals():
            bng.close()

if __name__ == "__main__":
    main()
