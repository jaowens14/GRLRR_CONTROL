import asyncio
from actuator import Actuator
from ultrasonic import Ultrasonic
from logger import Logger
from queues import Queues

async def ultrasonic_controller(ultrasonic: Ultrasonic, first_valid_event: asyncio.Event):
    """
    Runs the ultrasonic sensor loop. It continously waits on distance measurments from its queue,
    uses them to update the PID control for the drive motor speeds, and publishes speed commands.
    The very first time a reading in the valid range is seen, it signals the first_valid_event.
    """

    try:
        while True:
            #Wait for a new distance measurments
            distance = await ultrasonic.distance_queue.get()

            #Check if this measurment is valid (range 45 to 200mm)
            if not first_valid_event.is_set() and 45 < distance < 200:
                first_valid_event.set()
                ultrasonic.logger.log.info(f"First valid ultrasonic measurement recieved: {distance} mm")

            #Process the measurment (bad readings are replaces by the setpoint)
            ultrasonic.current_distance = ultrasonic.ignore_bad_measurements(distance)

            #If within the deadband, no correction is needed; otherwise run PID
            lower, upper = ultrasonic.correction_deadband
            if lower < ultrasonic.current_distance <= upper:
                u = 0
            else:
                u = ultrasonic.pid(ultrasonic.current_distance)

            ultrasonic.process_speed = round(max(ultrasonic.current_speed + u, 0), 4)
            ultrasonic.current_speed = ultrasonic.process_speed

            #Publish drive motor speed commands
            await ultrasonic.mcu_writes.put({"speed0": -1.0 * float(ultrasonic.process_speed)})
            await ultrasonic.mcu_writes.put({"speed1": -1.0 * float(ultrasonic.process_speed)})
            await ultrasonic.mcu_writes.put({"speed2": float(ultrasonic.process_speed)})
            await ultrasonic.mcu_writes.put({"speed3": float(ultrasonic.process_speed)})

            await asyncio.sleep(0.1)

    except asyncio.CancelledError:
        ultrasonic.logger.log.info("Ultrasonic controller cancelled")
        #On cancellation, send ero speed commands to all drive motors.
        for key in ["speed0", "speed1", "speed2", "speed3"]:
            await ultrasonic.mcu_writes.put({key: 0.0})
    except Exception as e:
        ultrasonic.logger.log.error(f"Error in ultrasonic controller: {e}")

async def actuator_sequence_controller(actuator: Actuator, first_valid_event: asyncio.Event, logger: Logger):
    """
    Waits for the first valid ultrasonic measurment and then starts a timer:
        - After 25s, it sets actuator 0 to 0V and immediately sets actuator 1 to 5v
        - After another 25s, it sets actuator 1 to 0V and actuator 2 to 5v
    """
    #Wait for the ultrasonic sensor to capture its first valid measurment
    await first_valid_event.wait()
    logger.log.info("Fist valid measurement detected. Starting actuator sequence timer")

    #Wait 25 seconds
    await asyncio.sleep(25)
    logger.log.info("25s elapser: Switching actuator 0 off and actuator 1 on.")
    await actuator.set_actuator_voltage(0, 0.0)
    await actuator.set_actuator_voltage(1, 5.0)

    #Wait 25 seconds
    await asyncio.sleep(25)
    logger.log.info("50s elapser: Switching actuator 1 off and actuator 2 on.")
    await actuator.set_actuator_voltage(1, 0.0)
    await actuator.set_actuator_voltage(2, 5.0)
