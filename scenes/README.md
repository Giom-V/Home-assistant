# Scenes

**Documentation:** <https://www.home-assistant.io/integrations/scene/>

Here are all the scenes for my lights. They are grouped by room, one file per
room.

## Detailled description

### [AllRooms.yaml](AllRooms.yaml)

Contains the scenes for all the inner house (not the ones in our solarium or
basement for ex.).

### [LivingRoom.yaml](LivingRoom.yaml)

Contains the scenes for living room lights. There are a couple of colored scenes
that we cycle using a [ikea
controller](https://www2.ikea.com/fr/fr/p/tradfri-telecommande-30443124/),
triggering [Automations](../automations/ikeaController.yaml), themselves
triggering some [Scripts](../scripts/livingroom.yaml).

I'm not using it anymore at the moment.

### [Party.yaml](Party.yaml)

The goal of this scene will be to set a festive mood with dim lights and music
reactive lighting.
