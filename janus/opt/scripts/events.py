import signal
import sys
import time

from pyhik.hikvision import HikCamera

from app.storage import add_event, get_camera


g_shutdown = False


class Sensor:
    def __init__(self, camera_name: str, camera: HikCamera, sensor: str, channel: str):
        self._camera_name = camera_name
        self._camera = camera
        self._sensor = sensor
        self._channel = channel

        self._state = None
        self._state_time = None

        self.update(1)

    def update(self, dummy_id):
        del dummy_id

        attributes = self._camera.fetch_attributes(self._sensor, self._channel)
        state = attributes[0]
        state_time = attributes[3].timestamp()

        if state is True:
            add_event(self._camera_name, self._sensor, int(state_time), None)
        elif self._state is True:
            add_event(
                self._camera_name, self._sensor, int(self._state_time), int(state_time)
            )

        self._state = state
        self._state_time = state_time


camera = None


def init():
    camera_name = sys.argv[1]
    camera_settings = get_camera(camera_name)

    if camera_settings["hik_url"] is None:
        return

    global camera
    camera = HikCamera(
        camera_settings["hik_url"],
        usr=camera_settings["hik_user"],
        pwd=camera_settings["hik_pass"],
    )

    camera.start_stream()

    for sensor, channel_list in camera.current_event_states.items():
        for channel in channel_list:
            camera.add_update_callback(
                Sensor(camera_name, camera, sensor, channel[1]).update,
                f"{camera.get_id}.{sensor}.{channel[1]}",
            )


def cleanup():
    if camera is not None:
        camera.disconnect()


if __name__ == "__main__":
    init()

    def signal_handler(sig, frame):
        if sig == signal.SIGINT or sig == signal.SIGTERM:
            global g_shutdown
            g_shutdown = True

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    while g_shutdown is False:
        time.sleep(0.1)

    cleanup()
