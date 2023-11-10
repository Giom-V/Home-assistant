# Home Assistant

![GitHub commit
activity](https://img.shields.io/github/commit-activity/w/Giom-V/Home-assistant)
![GitHub last
commit](https://img.shields.io/github/last-commit/Giom-V/Home-assistant)
[![CircleCI](https://dl.circleci.com/status-badge/img/gh/Giom-V/Home-assistant/tree/master.svg?style=shield)](https://dl.circleci.com/status-badge/redirect/gh/Giom-V/Home-assistant/tree/master)
[![Security Risk -
CoPilot](https://copilot.blackducksoftware.com/github/repos/Giom-V/Home-assistant/branches/master/badge-risk.svg)](https://copilot.blackducksoftware.com/github/repos/Giom-V/Home-assistant)
[![Codacy
Badge](https://api.codacy.com/project/badge/Grade/a5c5e4fe3edd434aad827e52ba9c69bc)](https://www.codacy.com/manual/Giom-V/Home-assistant?utm_source=github.com&utm_medium=referral&utm_content=Giom-V/Home-assistant&utm_campaign=Badge_Grade)

This is my personal home assistant configuration. I'm sharing it to provide the
community ideas on how to organize one's files and on which kind of automations
are feasible and how.

**Disclamer**: While I don't think it changes anything regarding how I manage my
home automations and what I'm sharing here, I prefer to be transparent and
reveal that I've recently starting to work for Google Nest and might be biaised
towards the Nest products. Taht said I was already using my Nest Doorbell and my
nest speakers/screens before joining so it's not like it changes anything.

## Organization of this GitHub

After staring like everybody with everything in my
[configuration](configuration.yaml) file, I started to split it to better keep
track of the changes using GitHub. I followed the example of
[@jonathanadams](https://github.com/jonathanadams/Home-Assistant-Configuration)
and split (or actually tried to since it's a work in progress) all the
configuration this way:

- basic configuration will stay in [configuration.yaml](configuration.yaml)
- every integration has its own yaml file in the [integrations](integrations/)
  folder
- when an integration corresponds to multiple entities
  ([lights](entities/lights/) for ex.), then they each have their own YAML file
  in the corresponding folder located in the [entities](entities/) folder.
- [scripts](scripts/), [automations](automations/) and [scenes](scenes/) are
  grouped by "theme" (everything related to a room or a device for ex.) in their
  corresponding folder. Each folder has or will have its own documentation to
  explain what each automation/script/scene does.

With things moving to the UI more and more it's becoming more and more
complicated to keep things organized but I'm trying my best.

## My devices

### Security

| Name                       | Type         | Brand   | Link | Integration                                                                      | Connectivity | Fully works?                                                        | Comment                                                                                                                                                                                          |
| -------------------------- | ------------ | ------- | ---- | -------------------------------------------------------------------------------- | ------------ | ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Nest Doorbell with battery | Doorbell     | Nest    |      | [Google Nest - Home Assistant](https://www.home-assistant.io/integrations/nest/) | WiFi         | Not really, you can't activate the camera by yourself               | If you can, avoid the battery one because charging it every 1/2 months is a hasle                                                                                                                |
| E1 Zoom                    | Camera       | Reolink |      | Reolink IP NVR/Camera                                                            | WiFi         | Yes, except you can't turn it on/off (I plan to use a plug instead) | Be carreful, the old model has the same name but doesn't have AI recognition so every bug passing by is triggering the motion detection. Also the cheaper E1 ,odel cannot be integrated into HA. |
| Shelly Flood               | Flood sensor | Shelly  |      | Shelly                                                                           | WiFi         | Yes, but not for long                                               | As much as I love shelly devices this one is really not good since the battery is being drained very fast:                                                                                       |
| Tile Mate                  | Tracker      | Tile    |      | Tile                                                                             | Bluetooth    | Yes                                                                 | I love the devices but you need enough users around so taht it works and at the moment there isn't as many as for AirTags                                                                        |
| Wyze Cam v2                | Camera       | Wyze    |      | Wyze                                                                             | WiFi         | Yes!                                                                | I really liked it, especially being able to switch it on/off, but it's harder to procure at a regular price in Europe so I had to switch to Reolink                                              |
| Dafang                     | Camera       | Xiaomi  |      |                                                                                  |              |                                                                     |

### Energy

| Name                 | Type           | Brand   | Link                                                                                                       | Integration       | Connectivity | Fully works?                                                           | Comment                      |
| -------------------- | -------------- | ------- | ---------------------------------------------------------------------------------------------------------- | ----------------- | ------------ | ---------------------------------------------------------------------- | ---------------------------- |
| Smart Radiator Valve | Radiator Valve | Netatmo | [https://www.netatmo.com/en-eu/smart-radiator-valves](https://www.netatmo.com/en-eu/smart-radiator-valves) | Netatmo / Homekit | WiFi         | Yes, except you can only see the temperature with a .5 degree precision | My wife finds it a bit noisy |
| Shelly plug S        |                | Shelly  |                                                                                                            | Shelly            | WiFi         | Yes!                                                                   | Great devices, affordable    |

### Lighting

| Name                | Type       | Brand       | Link | Integration     | Connectivity                                                             | Fully works?                  | Comment                                                                                              |
| ------------------- | ---------- | ----------- | ---- | --------------- | ------------------------------------------------------------------------ | ----------------------------- | ---------------------------------------------------------------------------------------------------- |
| Nanoleaf Shapes     | Lights     | Nanoleaf    |      | Nanoleaf / Rest | WiFi / Thread                                                            | Yes, with custom Rest command | I love them, especially the fact that I can trigger the sound reactive mode                          |
| Hue lightstrip plus | Lightstrip | Philips Hue |      | Philips Hue     | Zigbee through the Philipps hue gateways (which is pluges with ethernet) | Yes                           |                                                                                                      |
| Hue Smart button    | Remote     | Philips Hue |      | Philips Hue     | Zigbee through the Philipps hue gateways (which is pluges with ethernet) | Yes                           |                                                                                                      |
| Hue Tap Switch      | Remote     | Philips Hue |      | Philips Hue     | Zigbee through the Philipps hue gateways (which is pluges with ethernet) | Yes                           | Rarery it somehow doesn"t work but when it does it's great to think that it doesn't have any battery |

### Multimedia

| Name             | Type          | Brand        | Link | Integration               | Connectivity | Fully works?        | Comment                                                                                  |
| ---------------- | ------------- | ------------ | ---- | ------------------------- | ------------ | ------------------- | ---------------------------------------------------------------------------------------- |
| Google TV        | TV            |              |      | Android TV remote         | WiFi         | Yes, except the OSK | I think the integration prevents you from using the on-screen keyboard which is annoying |
| Chromecast Ultra | Set top box   | Google Nest  |      | Google Cast / Google Home | WiFi         | Yes                 |                                                                                          |
| Google Home      | Smart Speaker | Google Nest  |      | Google Cast / Google Home | WiFi         | Yes                 |                                                                                          |
| Google Home Mini | Smart speaker | Google Nest  |      | Google Cast / Google Home | WiFi         | Yes                 |                                                                                          |
| Nest Audio       | Smart Speaker | Google Nest  |      | Google Cast / Google Home | WiFi         | Yes                 |                                                                                          |
| Nest Hub         | Smart screen  | Google Nest  |      | Google Cast / Google Home | WiFi         | Yes                 |                                                                                          |
| Pixel Tablet     | Tablet        | Google Pixel |      | Google Cast / Google Home | WiFi         | Yes                 |                                                                                          |
| Player Pop       | Set top box   | Freebox      |      | Google Cast / Google Home | WiFi         | Yes                 |                                                                                          |
| Smart Clock      | Smart screen  | Lenovo       |      | Google Cast / Google Home | WiFi         | Yes                 |                                                                                          |

### Other

| Name                      | Type                 | Brand            | Link | Integration           | Connectivity | Fully works?                  | Comment                                                                                                                                                    |
| ------------------------- | -------------------- | ---------------- | ---- | --------------------- | ------------ | ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Brother L2710DW           | Printer              | Brother          |      | Brother Printer       | WiFi         | I guess                       | I'm not really using it TBH                                                                                                                                |
| Freebox delta             | Modem                | Freebox          |      | Freebox               | Ethernet     | Yes                           |                                                                                                                                                            |
| EV6                       | Car                  | Kia              |      | Hyundai / Kia Connect | 4G           | Yes but flaky                 | The integration is bit flaky but when it works it's great!                                                                                                 |
| My android phones         | Phones               | Mostly Pixels :) |      | Mobile App            | 4G           | Yes                           | The integration is great, I'm just unsre about how much it drains the battery                                                                              |
| Mutesync                  | "Presence detection" | Mutesync         |      | Mutesync              | WiFi         | Yes                           | This is a nice device to expose whether you are in a virtaul conference and oif your mic is on. That's just a pain to have to keeep the app open to do so. |
| Genius X                  | Toothbrush           | Oral-B           |      | Oral-B                | Bluetooth    | No, but I think it's my fault | The bathroom is very far from my raspberry Pi so I think the bluettoth connection doesn't always work                                                      |
| Connected washing machine | Washing machine      | Samsung          |      | SmartThings           | WiFi         | Yes                           | Let's be honnest, except for the power consumtion it's fairly useless at the moment                                                                        |
| Withings Scale            | Scale                | Withings         |      | Withings              | WiFi         | No                            | It works well but it forces me to renew the acess, for each person every 1 or 2 months which is way too much trouble                                       |
| Mi Air purifier 3C        | Air purifier         | Xiaomi           |      | Xiaomi Miio           | WiFi         | Yes                           | I'm really happy with it, I was worried it would be noisy but it's very quiet                                                                              |
| Roborock S5               | Robot Vaccum         | Roborock         |      | Xiaomi Miio           | WiFi         | Yes                           | I just love it, but by the S7 if you can since cleaning it is way easier                                                                                   |
| Roborock S7               | Robot Vaccum         | Roborock         |      | Xiaomi Miio           | WiFi         | Yes                           | I love it                                                                                                                                                  |

## Custom integrations

## Mobile app

After some time using [Ariela](http://ariela.surodev.com/) I then switched to
[HassKit](https://github.com/tuanha2000vn/hasskit). While it has a bit too much
an iOS-feel for me, I find it more convenient to be able to create specific
views for the mobile. Ariela was also not liking all the custom components and
the more I was customizing Lovelace, the more Ariela was becoming unusable. That
said, in the future, I might reuse Ariela to refurbish an old Android phone into
a new connected device.

Recently I've moved back to using the offical app since it also gives you the
opportunity to expose a lot of data from the phone to Home Assistant. My only
worry is that the battery consumption semms quite high, especially on my watch.
But maybe that's just an impression, I haven't really investigated.

## Continuous integration

I'm using [CircleCI](circleci.com) to check the configuration of every pull
request or every time something is pushed to the master branch. This is
configured in the [.cicleci/config.yml](.cicleci/config.yml) file but it's still
far from perfect checking lint raises way too many errors at the moment (likely
due to all the custom integrations, but I'm worried it won't work otherwise). It
was based on [@mhaak
work](https://github.com/mhaack/home-assistant-config/blob/master/.circleci/config.yml).

I used to use [Travis](https://travis-ci.org/) because it was free for open
source. But since it's not the case I've move top to [CircleCI](circleci.com).
That said you can still have a look at my Travis configuration in the
[.travis.yml](.travis.yml) file.

## Tracking work

I'm a former video game producer so I love Jira :D To keep my habits, I'm using
Jira to keep track of what I plan to do. It's integrated with github (my commits
and PR are linked to the Jira issues), slack (for notifications) and circleCI
for [continuous integration](#continuous-integration).

## Useful links and thanks

- [hacf.fr](hacf.fr) - French Home Asssitant community
- [zigbee.blakadder.com](zigbee.blakadder.com) - Zigbee devices compatibility
  database
