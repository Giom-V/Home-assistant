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

### [Air purifier](air_pirifier.yaml)

Those automations are related to my air purifier located in my office. That's
the reason why their are all using the `input_boolean.working` value that
indicates if I'm working in my office or not. That value is managed in
[`working.yaml`](#working), documented below.

There are 3 automations:

- `Turn on Air Purifier when I start working`: As its name implies starts the
  air purifier when I start working.

- `Turn off Air Purifier when I'm off`: Turns it off when I stop working

- `Turn off Air purifier for a while if the air quality is good`: In case the
  air quality is good enough (PM5 under 2 for 5mn), I then turn off the air
  purifier until it becomes bad (PM5 over 5) for at least 15mn. This is meant to
  save energy and extend filters life.

### [Alerts](alerts.yaml)

Those automations are meant to alert me if something weird is going on, eg. an
abnormal temperature.

There are currently only 2 automations:

- `Alert me if the temperature is too low`: In case the temperature in any of
  the indoor rooms (including the basement) goes below 10 degrees, alert me
  through Google Chat and my Google Homes.

- `Alert me if the temperature is too high`: Same if the temperature goes over
  30 (to be tweaked since I think it happens quite frequently in summer)

I also used to have automations related to noise and moisture but they were
using my [Minut Point](minut.com) devices but since I can't inteface them with
HA I had to get rid of the automations. I also used to have 2 automations
related to my freezer, using a door sensor because my daughter used to forget to
close it, but I now have a new freezer which beeps so I also disabled the
automations. I'm still keeping them all here as reference.

#### Future improvements for alerts

- Maybe having different upper values for the temperature depending on the
  seasons
- I should group all temperature sensors in a group so that I won't have to list
  them all in each automation
- Leak detection

### [Away mode](away_mode.yaml)

Those automations are also related to something unexpected happening at home,
but the caveat with the [alerts](#alerts) is that those ones should not trigger
if somebody is at home. They are mostly related to multiple ways of detecting
presence, from the using cameras or motion sensors to lights being switched on.

There are also some tentative for presence simulation.

All those automations are using the 3 helpers

- `binary_sensor.people_home` indicates if someone who's tracked (my wife and I)
  are home. The issue is that it doesn't take into account that my daughter
  could be [home alone](https://en.wikipedia.org/wiki/Home_Alone), which for now
  doesn not happen often since she's still young or that we may have visitors
  (my parents or my in-laws for ex.), which is a case that happen quite often.

- [`input_boolean.visitors`](visitors.md) is meant to solve that problem. It
  indicates that we have someone visiting and prevents the different
  automations from triggering.

- `input_boolean.away_mode` indicates that the "alarm/alerts" are set. Using
  such a helper lets us clearly see the status and also let us overwrite it if
  needed.

All those helpers are exposed to Google home so that we can easily
switch/overwrite them.

The different automations are:

- [`Switch Away mode on when we are away for more than an hour`](away_mode.yaml#L58):
  This is the automation that switches the `input_boolean.away_mode` value to
  on when we are away, this then enables all the other automations. There's a
  slight delay to prevent the alarm to switch too often, to cover for when we
  leave our daughter for a short while, or if the geofencing becomes flaky and
  our home/away presence switches.

- [`Switch Away mode off when we come back`](away_mode.yaml#L82): This is the
  reverse automation, setting off `input_boolean.away_mode` and the alerts. It
  also sets the media players volumes back to normal since the alerts are
  raising them to the maximum.

- `Switch motion detection and alarms on when the away mode is on` and `Switch
  motion detection off when the away mode is off`: These used to switch the
  motion detection of my Dafang camera on and off when we were home/away, but
  that's not possible with my new Reolink cameras so I disabled the
  automations.

- [`Motion detected`](away_mode.yaml#L107): Sends an alert (via Google Chat),
  and shout through all the media players if motion is detected by one of the
  cameras. Mode is `single` because I don't want the script to restart if
  motion is continuously detected.

- [`Door openned while away`](away_mode.yaml#L182): Does the same thing but if a
  door is opened.

- [`Mouvement detected while away`](away_mode.yaml#L254): Same again but if one
  of the motion sensors sees something.

- [`Lights switched on while away`](away_mode.yaml#L305): Same with lights being
  switched on, the problem being that we also want to switch on the lights for
  presence detection, so for now the lights used for the presence are not in
  this automation.

- [`Presence simulation Bureau`](away_mode.yaml#L338): Presence detection in my
  office. It uses randomness for more realness. Starts at a random time between
  30 before sunset and 15mn after and ends between 11PM and 11:15PM.

- [`Presence simulation Aurore's bedroom`](away_mode.yaml#L365): Same thing but
  with slightly different times (the worst that could happen would be to have
  all lights switching on and off at the same time).

- [`Reboot HA every week when we are away`](away_mode.yaml#L392): This one is a
  failsafe. When I'm away for a long time I want to be certain HA is not
  frozen, so I like to reboot it at least once a week. I also have a Shelly
  plug that I program to reboot the modem every week for the same reason.

A more detailed documentation of those automations can be found in the
[`alarms.md`](alarms.md) file.

#### Future improvements for the away mode

- Use a scene to set the volume of the media players back when we come back
  (except it might not work with "all")
- Switch off the TV after the alerts
- Switch cameras on/off depending on the away state instead of jsut the motion
  detection
- Use app notifications for the alerts
- Send pictures alongside the notifications when something is detected by the
  cameras
- Find a way to have both the lights alert and presence detection
- Continue to improve presence simulation (TV, or rando; colars in the living
  room to simulate it)

### [Car](car.yaml)

These are all the automations related to my car and its charger since I only
want to charge it during off-peak hours (and later on when producing a surplus
of electricity with panels).

The automations are:

- `Turn on the car's chargeur only during off-peak hours`: Switches on/off the
  plug controlling the car charger depending on the off-peak hours. I'm quite
  satisfied to have managed to do that in one automation instead of two.

- `Preheat the car`: In winter, on school days, and if we are home, if the
  temperature is low, preheat the car just before when we have to go to school.

- `Lock car when at home for at least an hour`: I very often forget to close my
  car's door so this is a failsafe.

- `Reload Kia integration when it's down`: Sadly the Kia integration can but
  flaky so this aims at making things better.

There's also a bunch of automations related to logging my car consumption but
since they don't work at the moment you should just ignore them.

#### Future improvements for the car

- Add a failsafe when HA is booted to check on the off-peak hours and set the
  charger status accordingly
- Only preheat the car if it's not a holiday (using the calendar integration)

### [Meetings](meetings.yaml)

Theses automations are meant to switch a light colors depending on if I'm in a
meeting and if I'm talking (using the [Mutesync](mutesync.com) device and
integration), but since I have set it up since my last move I'm not going to
comment on it. It's quite straightforward so it shouldn't be hard to understand.

### [Night Time](nightTime.yaml)

These are old automations that I'm not using anymore and just keeping for
reference. There were all meant to switch on some lights and changing thjeir
colors to give a hint to my daughter on whether it was time for the night
routine or to go to bed.

### [Others](others.yaml)

Miscellaneous automations, mostly (all?) related to lights, which were not
fitting anywhere else.

These are:

- `Switch off lights 30mn after sunrise` and `Switch off lights 60mn after
  sunrise`: Except maybe for my office, all lights should be switched off during
  the day so this is what those automations do (just slightly later during the
  Canadian winter).

- `Switch off all lights when we go to bed`: Switches off all lights when it's
  time to go to bed (time set up in the `input_datetime.nighttime_end` helper)
  so that it forces us to do so instead of forgetting the time while watching a
  serie.

- `Switch off all lights when nobody's home for 30mn`: There's no need for
  lights if nobody is home.

#### Future improvements

- Not switching off lights if we have visitors

### [Vaccum cleaner](vacuumCleaner.yaml)

Here are all the automations related to my vacuum cleaner.

Note that some of the logic is managed in [scripts](../scripts/), in the
[`vacuum.yaml`](../scripts/vacuum.yaml) file.

Some automations were related to the IFTT integration but since [Google removed
the option for IFTTT to parce custom
commands](https://ifttt.com/explore/google-assistant-changes), I had to get rid
of them. Initially they were letting me say "OK Google, Clean the bedroom 3
times", and the string "the betroom 3 times" was passed down to HA, parsed (cf.
[scripts](../scripts/vacuum.yaml)) and then the right command was sent to the
vaccum.

The remaining automations are:

- `Start Cleaning Room`: I have a selector name `input_select.vacuum_room` which
  contains all the rooms in the house, selecting a room triggers the cleaning of
  it. I'm not really using it often but keeping it just in case.

- `vacuum Kitchen and dining room when we are away`: This one is a very basic
  automation that starts the vaccum at a fixed time if we are not home. It's not
  used anymore but kept as a reference. It was good enough when we were both
  working at the office but not anymore.

- `vacuum Kitchen and dining room when we are away (Covid version)`: It's the
  advanced version, named "Covid" because I started to work home during the
  pandemic. It waits for us to be away for 5mn (the timer is short because I was
  it to start while I'm bringin my daughter to school in the morning). Then if
  we do not have visitors, or if its' not too late or too early, if it's a
  worked day (in which case only 1 of us needs to be away) or not (in which case
  we need to be both away), and finally if it had not done any cleaning in the
  last 12h, it starts vaccuming the kitchen, the dining room and the bathroom.
  This is my most complicated automation, at least in regard to conditions.

- `Update the time of the last cleaning`: I'm tracking in
  `input_datetime.last_vacuum` the last time the vaccum cleaner has been doing
  its job, so taht I'm not triggering it more than every 12h. That automation
  save the time whenever the vaccum is used.

- `Start/stop xiaomi fast scan interval` and `Update xiaomi map extractor`: The
  [Xiaomi
  integration](https://www.home-assistant.io/integrations/xiaomi_miio/#xiaomi-mi-robot-vacuum)
  stops working if it receives too many calls per day and the [map
  extractor](https://github.com/PiotrMachowski/Home-Assistant-custom-components-Xiaomi-Cloud-Map-Extractor)
  one is making a lot of calls if we want to be able to follow the vacuum on the
  map in real time. So that two automations work together to only update the map
  when one of the vacuum is in use.

#### Future improvements for the vaccum cleaner

- Treat holidays as non-working days (using the calendar integration)
- Still vacuum even if we are here if no cleaning has been done for days
- Find a way to be able to tell the vacuum not to vaccum right now but to do it
  later
- Use "And/Or" instead of multiple ifs to make the `Update xiaomi map extractor`
  automation easier to read
- Prevent/Delay the vacuum from starting if I'm at home and in a call

### [Working](working.yaml)

These automations goal is to set the value of `input_boolean.working` depending
on different signals to indicate if I'm working or not and impact other
automations accordinly.

`input_datetime.work_start` and `input_datetime.work_end` indicate my usual
working hours.

At the moment:

- `Sets that I'm working when I'm at home`: Says I'm working at the begining of
  my shift if I'm at home.

- `Sets that I'm not working when I leave`: I stop working if I'm not at home
  (went running or just to the school)

- `Sets that I'm working when I come back`: Back at work when I'm back

- `Sets that I stop working at the end of my shift`: End my working time at the
  time entered in `input_datetime.work_end`.

#### Future improvements for the working indicator

- Use my computer status and meet status as an extra signal.

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
