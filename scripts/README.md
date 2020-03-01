# Scripts

**Documentation:** <https://www.home-assistant.io/integrations/script/>

Here are all the scenes for my lights. They are grouped by function and more or less corresponds to similarity-named files in the [automation](../automations) folder.

## Detailled description

### [Livingroom.yaml](livingroom.yaml)

There are two scripts there. One to change the [scene](../scenes/LivingRoom.yaml) depending of the value in the `input_select.living_room_color` select in Lovelace.
The other script cycle between the [colored scenes](../scenes/LivingRoom.yaml) when the [Tradfri controller](https://www2.ikea.com/fr/fr/p/tradfri-telecommande-30443124/) is pressed.

### [Timelapse.yaml](timelapse.yaml)

Those scripts are meant to send pictures of the sunset/sunrise on Slack everyday.
There's also another script that should be creating a daily gif and send it to slack but it doesn't work at the moment.

### [Vacuum.yaml](vacuum.yaml)

The first script (`vacuum_dispatch`), looks for keywords in the text received from IFTTT through a webhook (managed by the [`IFTTT_zone_cleaning_webhook` automation](../automations/vacuumCleaner.yaml)) and then runs one of the other scripts depending on the rooms that we want to clean.

This was based on [this post](https://community.home-assistant.io/t/howto-xiaomi-vacuum-zoned-cleaning/51293) from [ciB](https://community.home-assistant.io/u/ciB).
