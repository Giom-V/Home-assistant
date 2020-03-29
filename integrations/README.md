# Integration

**Documentation:** <https://www.home-assistant.io/docs/configuration/splitting_configuration/>

Here we have a file per "integration". The can be very simple (a couple of line to give an token for ex.). But if they related to multiple other integrations, devices or entities, they usually point with a folder the [entities](../entitites) one where each of their sub-entities are listed.

## Core integrations

### [Discovery.yaml](discovery.yaml)

**Documentation:** <https://www.home-assistant.io/integrations/discovery/>

Discovers and automatically configures zeroconf/mDNS and UPnP devices on your network.

### [Http.yaml](http.yaml)

**Documentation:** <https://www.home-assistant.io/integrations/http/>

Manages the server url and port, as well as the SSL connection.

### [Logbook.yaml](logbook.yaml)

**Documentation:** <https://www.home-assistant.io/integrations/logbook/>

Web interface to keep track of everything that happens in Home Assistant. It depends on the recorder integration (currently using the default settings of it in my case).

### [Logger.yaml](logger.yaml)

**Documentation:** <https://www.home-assistant.io/integrations/logger/>

Defines the level of logging activities in Home Assistant so that we can get more logs for specific components.

### [Map.yaml](map.yaml)

**Documentation:** <https://www.home-assistant.io/integrations/map/>

Enables a map on the frontend to display the location of tracked devices.

### [Mobile_app.yaml](mobile_app.yaml)

**Documentation:** <https://www.home-assistant.io/integrations/mobile_app/>

Allows Home Assistant mobile apps to easily integrate with the Home Assistant server (in my case, [HassKit](https://github.com/tuanha2000vn/hasskit))

### [Updater.yaml](updater.yaml)

**Documentation:** <https://www.home-assistant.io/integrations/updater/>

Binary sensor that checks daily for new releases of Home Assistant.

## More-complex integrations

### [Camera.yaml](camera.yaml)

**Documentation:** <https://www.home-assistant.io/integrations/camera/>

Point to the (cameras)[../entities/cameras] folder where each of the (two) camera are set-up.

### [Google_assistant.yaml](google_assistant.yaml)

**Documentation:** <https://www.home-assistant.io/integrations/google_assistant/>

Enable the integration with Google Assistant. At the moment I mainly use it to expose zigbee devices to Google Assistant so that I can control them with my Google Homes.

### [Input_boolean.yaml](input_boolean.yaml)

**Documentation:** <https://www.home-assistant.io/integrations/input_boolean/>

### [Linky.yaml](linky.yaml)

**Documentation:** <https://www.home-assistant.io/integrations/linky/>

### [Sensors.yaml](sensors.yaml)

**Documentation:** <https://www.home-assistant.io/integrations/sensor/>

### [Sun.yaml](sun.yaml)

**Documentation:** <https://www.home-assistant.io/integrations/sun/>

### [Weather.yaml](weather.yaml)

**Documentation:** <https://www.home-assistant.io/integrations/weather/>
