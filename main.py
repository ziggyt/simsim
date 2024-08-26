import logging
import random

import beamngpy.api.beamng.ui
from beamngpy import BeamNGpy, Scenario, Vehicle
from beamngpy.api.beamng.ui import UiApi
import math
import time


run_at_home = False

bng_home = run_at_home ? r'"C:\Users\max\Documents\BeamNG.tech.v0.32.5.0\BeamNG.tech.v0.32.5.0' : r'C:\Users\CAPsim\Documents\beamng'


def main():
    # Set up logging
    logging.basicConfig(level=logging.DEBUG)

    # Specify the path to your BeamNG.tech installation

    # beamng_home = r" # Path for running scenario at home
    try:
        # Connect to BeamNG.tech
        bng = BeamNGpy('localhost', 64256, home=bng_home, user=r'C:\Users\CAPsim\Documents\beamng\BeamNG.tech.v0.31.2.0\tech\max')
        bng.open(launch=True)

        logging.info("Connected to BeamNG.tech")

        # Create a scenario in East Coast USA map
        scenario = Scenario('east_coast_usa', 'Driver Impairment User Test v0.1', description='Here we can add some simple instructions if we want to.', authors='RISE', settings={'Start Time': 0})

        # Player spawn point coordinates
        player_spawn = (438.334015, -810.008179, 42.9711952)

        # Player rotation (180 degrees from previous rotation)
        player_rot_quat = (0.0087653, 0.00096168, 0.93361151, 0.35821542)

        # Create and add the player's vehicle
        player_vehicle = Vehicle('ego_vehicle', model='etk800', license='RISE')
        scenario.add_vehicle(player_vehicle, pos=player_spawn, rot_quat=player_rot_quat)

        # NPC vehicles information
        npc_vehicles = [
            {
                'name': 'npc1',
                'pos': (306.621948, -641.772888, 37.067379),
                'rot': (0.0425180085, -0.0719198063, 0.864066243, 0)  # Converted to quaternion
            },
            {
                'name': 'npc2',
                'pos': (25.9974442, -341.749786, 42.8027916),
                'rot': (0.0425180085, -0.0719198063, 0.864066243, 0)  # Converted to quaternion
            },
            {
                'name': 'npc3',
                'pos': (-242.363251, -32.2967873, 32.012085),
                'rot': (0.0425180085, -0.0719198063, 0.864066243, 0)  # Converted to quaternion
            },
            {
                'name': 'npc4',
                'pos': (909.38092, -272.285278, 40.5305939),
                'rot': (0, 0, -0.042764, 0.999085)
            }
        ]


        # Create and add NPC vehicles
        for npc in npc_vehicles:
            vehicle = Vehicle(npc['name'], model='etk800', license=f'NPC {npc["name"][-1]}')
            scenario.add_vehicle(vehicle, pos=npc['pos'], rot_quat=npc['rot'])

        logging.info("Vehicles added to scenario")

        # Load the scenario
        scenario.make(bng)
        logging.info("Scenario created")

        # Load the scenario in BeamNG.tech
        bng.load_scenario(scenario)
        logging.info("Scenario loaded in BeamNG.tech")

        # Set up initial state
        player_vehicle.ai.set_mode('manual')
        for npc in npc_vehicles:
            scenario.get_vehicle(npc['name']).ai.set_mode('disabled')
        logging.info("Vehicle AI modes set")

        # Set the default camera to interior view
        bng.camera.set_player_mode(player_vehicle, 'driver', {'fov': 60})
        logging.info("Camera set to interior view")

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

        npc_triggered = [False] * len(npc_vehicles)

        while True:
            # Update vehicle states
            scenario.update()

            # Get player position
            player_pos = player_vehicle.state['pos']

            for i, npc in enumerate(npc_vehicles):
                npc_vehicle = scenario.get_vehicle(npc['name'])
                npc_pos = npc_vehicle.state['pos']

                # Calculate distance between player and NPC
                distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(player_pos, npc_pos)))

                # If player is closer than 180 meters and NPC hasn't been triggered yet, make NPC drive
                if distance < 180 and not npc_triggered[i]:
                    npc_vehicle.ai.set_mode('traffic')
                    npc_vehicle.ai.drive_in_lane(True)
                    npc_vehicle.ai.set_speed(12, mode='limit')  # Set speed limit to 12 m/s (about 43 km/h or 27 mph)

                    npc_pos = [npc_pos[0] + 2, npc_pos[1] + 2, npc_pos[2] + 2]
                    print(npc_pos)
                    print("\n\n\n\n\n\n\n\n\n\n\n\n")

                    npc_triggered[i] = True
                    logging.info(f"{npc['name']} has been triggered and is now driving in traffic mode!")
                    #UiApi.display_message(msg=f"Overtake the vehicle in front of you")
                    bng.ui.display_message(f"Overtake the vehicle in front of you")
                    time.sleep(0.2)
                    bng.ui.display_message(f"Overtake the vehicle in front of you")
                    time.sleep(0.2)
                    bng.ui.display_message(f"Overtake the vehicle in front of you")

            time.sleep(0.1)

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)
    finally:
        # Close the connection
        if 'bng' in locals():
            bng.close()

if __name__ == "__main__":
    main()
