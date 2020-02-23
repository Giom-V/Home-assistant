# Home Assistant 
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/Giom-V/Home-assistant)
![GitHub last commit](https://img.shields.io/github/last-commit/Giom-V/Home-assistant)
[![Build Status](https://travis-ci.com/Giom-V/Home-assistant.svg?token=c6vDr93ZdPMNjFeVzhDo&branch=master)](https://travis-ci.com/Giom-V/Home-assistant)

Personal home assistant configuration.

## Organization of this GitHub
After staring like everybody with everything in my [configuration](configuration.yaml) file, I started to split it to better keep track of the changes using GitHub. I followed the example of [@jonathanadams](https://github.com/jonathanadams/Home-Assistant-Configuration) and split (or actually tried to since it's a work in progress) all the configuration this way:
- basic configuration will stay in [configuration.yaml](configuration.yaml)
- every integration has its own yaml file in the [integrations](integrations/) folder
- when an integration corresponds to multiple entities ([lights](entitites/lights/) for ex.), then they each have their own YAML file in the corresponding folder located in the [entitites](entitites/) folder.
- [scripts](scripts/), [automations](automations/) and [scenes](scenes/) are grouped by "theme" (everything related to a room or a device for ex.) in their corresponding folder

## My devices
| Name | Type | Brand | Picture | Link | Integration |
|------|------|-------|---------|------|-------------|
|      |      |       |         |      |             |
|      |      |       |         |      |             |
|      |      |       |         |      |             |

## Custom integrations


## Mobile app
After some time using [Ariela](http://ariela.surodev.com/) I recently switched to [HassKit](https://github.com/tuanha2000vn/hasskit). While it has a bit too much an iOS-feel for me, I find it more convenient to be able to create specific views for the mobile. Ariela was also not liking all the custom components and the more I was customizing Lovelace, the more Ariela was becoming unusable. That said, in the future, I might reuse Ariela to refurbish an old Android phone into a new connected device.

##  Continuous integration
At the moment I'm only using [Travis](https://travis-ci.org/) to check the configuration every time something is pushed to the master branch. This is configured in the [.travis.yml](.travis.yml) file.

## Useful links and thanks


