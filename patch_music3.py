import sys

filepath = 'automations/chambre_aurore.yaml'
with open(filepath, 'r') as file:
    content = file.read()

# Replace the specific block of automation
old_block = """- id: "ha_63_aurore_meditation"
  alias: Aurore's meditation music
  description: "Joue un album de méditation pour Aurore"
  trigger:
    - platform: time
      at: "22:00:00"
  condition: []
  action:
    - action: mass.play_media
      target:
        entity_id: media_player.enceinte_aurore_2
      data:
        media_id: >
          {{ [
            "imagine que tu es un animal",
            "imagine que tu as des super pouvoirs"
          ] | random }}
        media_type: track
        enqueue: play
  mode: single"""

new_block = """- id: "ha_63_aurore_meditation"
  alias: Aurore's meditation music
  description: "Joue un album de méditation pour Aurore"
  trigger:
    - platform: time
      at: "22:00:00"
  condition: []
  action:
    - action: mass.play_media
      target:
        entity_id: media_player.enceinte_aurore_2
      data:
        media_id: >
          {{ [
            "imagine que tu es un animal",
            "imagine que tu as des super pouvoirs"
          ] | random }}
        media_type: album
        enqueue: play
        radio_mode: true
  mode: single"""

# Update content
if old_block in content:
    content = content.replace(old_block, new_block)
    with open(filepath, 'w') as file:
        file.write(content)
    print("Replaced successfully")
else:
    print("Block not found!")
