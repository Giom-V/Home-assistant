# Automations

This folder contains all of my organized automations along with some
explanations of what I do and why.

Please note that automations are not the only way to automate things in Home
Assistant. Some of the magic is also managed through [scripts](../scripts),
[template sensors](../configuration.yaml?l=60), [custom
integrations](../custom_components) or add-ons.

Also, I used to have more automations when I was in Canada but since I'm moved
mutiple times during the last 2 years I did not had time to bring them all back
(some also don't make sense anymore). They are still in a
[branch](https://github.com/Giom-V/Home-assistant/tree/620sapins-rpi3b-hassbian/automations)
I created when I moved.

Since I'm usually documenting way after writting the automations I also
sometimes add ideas on how I could have made them better.

## WIP/Prototypes

I usually prototype or start my automations using the UI editor, so my WIP
automations are usually located in the root
[automations.yaml](../automations.yaml) file. They should also normally be in a
branch and in a pull request so it should be transparent to whoever only looks
at my master branch. But sometimes I'm lazy so the file isn't always (well...
rarely) empty as it should be.

## Set-up

The way I'm managing having this folder with different files who contains
automations, and on top of that keeping the root
[automations.yaml](../automations.yaml) file is that way:

- in the main [configuration.yaml](../configuration.yaml), this line `packages:
  !include_dir_named integrations` makes it so each integration has its own file
  in the [integrations/](../integrations/) folder.

- in the [integrations/](../integrations/) folder we have a
  [automations.yaml](../integrations/automations.yaml) file.

- in this [automations.yaml](../integrations/automations.yaml) we first load
  everything from this [automations/](../automations/) folder using this line:
  `automation manual: !include_dir_merge_list ../automations/`

- the next line, `automation ui: !include ../automations.yaml` loads the root
  [automations.yaml](../automations.yaml) file

## My automations

### [Alerts](alerts.yaml)

Those automations are meant to alert me if something weird is going on, eg. an
abnormal temperature, a leak, or an unexpected presence.

### [Away mode](away_mode.yaml)

Those automations are related to things happening at home while we are away.
They are mostly related to multiple ways of detecting presence, from using
cameras or motion sensors to lights being switched on. There are also some
tentative for presence simulation.

### [Cannes](cannes.yaml)

Automations specific to the Cannes location, mostly for security and
monitoring.

### [Car](car.yaml)

These are all the automations related to my car and its charger since I only
want to charge it during off-peak hours (and later on when producing a surplus
of electricity with panels).

### [Covers](covers.yaml)

Automations for controlling the covers (shutters, blinds) based on sun
position and other conditions.

### [Lights](lights.yaml)

General automations for controlling the lights, such as turning them on at
sunset or off when nobody is home.

### [Meetings](meetings.yaml)

Theses automations are meant to switch a light colors depending on if I'm in a
meeting and if I'm talking (using the [Mutesync](mutesync.com) device and
integration).

### [Night](night.yaml)

Automations that run at night, like turning off all the lights and devices.

### [Night Time](nightTime.yaml)

These are old automations that I'm not using anymore and just keeping for
reference.

### [Office](office.yaml)

Automations related to my office, like turning on a light when I'm in a
meeting.

### [Plugs and Energy](plugs_and_energy.yaml)

Automations for managing smart plugs and monitoring energy consumption.

### [Pond and Water](pond_and_water.yaml)

Automations for the garden pond pump and the main water valve.

### [Remotes](remotes.yaml)

Automations triggered by physical remotes (like ZHA or MQTT buttons) to
control various devices.

### [Vaccum cleaner](vacuumCleaner.yaml)

Here are all the automations related to my vacuum cleaner. Note that some of
the logic is managed in [scripts](../scripts/), in the
[`vacuum.yaml`](../scripts/vacuum.yaml) file.

### [Working](working.yaml)

These automations goal is to set the value of `input_boolean.working` depending
on different signals to indicate if I'm working or not and impact other
automations accordinly.

## Ideas

Some ideas of automations I want to add later on:

- Detecting if I forgot to take out the trash
- Good night routine which switches off lights, close curtains, and tell me if a
  door is open
- good morning routine, with also a summary of my day (do I have a lunch
  planned, is it me or my wife who's in charge of my daughters activities,
  etc...)
- Detect if a car approches the house (I want to be able to say "I'm waiting for
  someone, tell me when they arrive")
- Circadian lights
- Party mode (setting all lights in music modes if possible, off if not)
- Reminder if it's past the end of school time and nobody seems to be at the
  school
- "You have mail" notification using a sensor in my mailbox
- Smart heating
- More proactive notifications with CTA like receiving a chat messages that says
  "According to your calendar, your visitors should have left, should I
  deactivate the visitor mode?".
- Redo what I was doing in Canada with a remote that was switching between
  different scenes in my living-room (for ref.
  [automations](https://github.com/Giom-V/Home-assistant/blob/620sapins-rpi3b-hassbian/automations/ikeaController.yaml),
  [scripts](https://github.com/Giom-V/Home-assistant/blob/620sapins-rpi3b-hassbian/scripts/livingroom.yaml)
  and
  [scenes](https://github.com/Giom-V/Home-assistant/blob/620sapins-rpi3b-hassbian/scenes/LivingRoom.yaml))
