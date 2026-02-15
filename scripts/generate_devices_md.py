import json
import os
import sys
from collections import defaultdict

# Define paths
CONFIG_DIR = "/config"
if not os.path.exists(CONFIG_DIR):
    CONFIG_DIR = "."  # Fallback for local testing

AREA_REGISTRY_FILE = os.path.join(CONFIG_DIR, ".storage/core.area_registry")
DEVICE_REGISTRY_FILE = os.path.join(CONFIG_DIR, ".storage/core.device_registry")
ENTITY_REGISTRY_FILE = os.path.join(CONFIG_DIR, ".storage/core.entity_registry")
OUTPUT_FILE = os.path.join(CONFIG_DIR, "devices.md")

def load_json(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        return None
    except json.JSONDecodeError:
        print(f"Error: JSON decode error in file: {filepath}", file=sys.stderr)
        return None

def get_entity_status(entity):
    if entity.get('disabled_by'):
        return ' (Disabled)'
    if entity.get('hidden_by'):
        return ' (Hidden)'
    return ''

def write_area_details(f, area, area_devices, device_entities, area_entities):
    f.write(f"### Area: {area['name']} ({area['id']})\n\n")

    # List devices in this area
    if area['id'] in area_devices:
        sorted_devices = sorted(area_devices[area['id']], key=lambda x: x['name'] or x['name_by_user'] or "Unknown")
        for device in sorted_devices:
            name = device['name_by_user'] or device['name'] or "Unknown Device"
            manufacturer = device.get('manufacturer', 'Unknown')
            model = device.get('model', 'Unknown')
            f.write(f"- **Device:** {name} ({manufacturer} {model})\n")

            # List entities for this device
            if device['id'] in device_entities:
                for entity in sorted(device_entities[device['id']], key=lambda x: x['id']):
                    status = get_entity_status(entity)
                    f.write(f"  - Entity: `{entity['id']}` ({entity['name']}){status}\n")
            else:
                    f.write("  - *No entities*\n")
    else:
        f.write("- *No devices in this area*\n")

    # List standalone entities in this area (no device)
    if area['id'] in area_entities:
        f.write("- **Standalone Entities:**\n")
        for entity in sorted(area_entities[area['id']], key=lambda x: x['id']):
                status = get_entity_status(entity)
                f.write(f"  - Entity: `{entity['id']}` ({entity['name']}){status}\n")

    f.write("\n")

def main():
    areas_data = load_json(AREA_REGISTRY_FILE)
    devices_data = load_json(DEVICE_REGISTRY_FILE)
    entities_data = load_json(ENTITY_REGISTRY_FILE)

    if not areas_data or not devices_data or not entities_data:
        print("Error: Could not load one or more registry files.", file=sys.stderr)
        sys.exit(1)

    # Process Areas
    areas = {} # id -> area object
    for area in areas_data['data']['areas']:
        areas[area['id']] = area

    # Process Devices
    devices = {} # id -> device object
    area_devices = defaultdict(list) # area_id -> list of devices
    orphan_devices = []

    for device in devices_data['data']['devices']:
        devices[device['id']] = device
        area_id = device.get('area_id')
        if area_id:
            area_devices[area_id].append(device)
        else:
            orphan_devices.append(device)

    # Process Entities
    device_entities = defaultdict(list) # device_id -> list of entities
    orphan_entities = [] # entities without device (and potentially without area, or area overrides)
    area_entities = defaultdict(list) # area_id -> list of entities (that have area but no device, or override)

    for entity in entities_data['data']['entities']:
        device_id = entity.get('device_id')
        area_id = entity.get('area_id')

        # Helper to simplify entity processing
        entity_obj = {
            'id': entity['entity_id'],
            'name': entity.get('name') or entity.get('original_name'),
            'disabled_by': entity.get('disabled_by'),
            'hidden_by': entity.get('hidden_by'),
            'platform': entity.get('platform')
        }

        if device_id:
            device_entities[device_id].append(entity_obj)
        elif area_id:
             area_entities[area_id].append(entity_obj)
        else:
            orphan_entities.append(entity_obj)

    # Structure for output: Floor -> Area -> Device -> Entities
    # We need to group areas by floor first.
    floors = defaultdict(list) # floor_id -> list of areas
    # Get unique floor IDs from areas
    # Note: 'floor_id' is a string in area object.

    # Also handle areas with no floor
    no_floor_areas = []

    for area_id, area in areas.items():
        floor_id = area.get('floor_id')
        if floor_id:
            floors[floor_id].append(area)
        else:
            no_floor_areas.append(area)

    # Generate Markdown
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("# Devices and Entities\n\n")
        f.write("This file is automatically generated. Do not edit manually.\n\n")

        # Sort floors alphabetically (or by some order if known, but alphabetical is safe)
        sorted_floors = sorted(floors.keys())

        for floor_id in sorted_floors:
            f.write(f"## Floor: {floor_id.capitalize()}\n\n")

            # Sort areas in this floor
            sorted_areas = sorted(floors[floor_id], key=lambda x: x['name'])

            for area in sorted_areas:
                write_area_details(f, area, area_devices, device_entities, area_entities)

        # Handle areas with no floor
        if no_floor_areas:
            f.write("## No Floor Assigned\n\n")
            sorted_areas = sorted(no_floor_areas, key=lambda x: x['name'])
            for area in sorted_areas:
                write_area_details(f, area, area_devices, device_entities, area_entities)

        # Handle Orphan Devices (no area)
        if orphan_devices:
             f.write("## Orphan Devices (No Area)\n\n")
             sorted_devices = sorted(orphan_devices, key=lambda x: x['name'] or x['name_by_user'] or "Unknown")
             for device in sorted_devices:
                name = device['name_by_user'] or device['name'] or "Unknown Device"
                manufacturer = device.get('manufacturer', 'Unknown')
                model = device.get('model', 'Unknown')
                f.write(f"- **Device:** {name} ({manufacturer} {model})\n")

                if device['id'] in device_entities:
                    for entity in sorted(device_entities[device['id']], key=lambda x: x['id']):
                        status = get_entity_status(entity)
                        f.write(f"  - Entity: `{entity['id']}` ({entity['name']}){status}\n")
                else:
                        f.write("  - *No entities*\n")

        # Handle Orphan Entities (no device, no area)
        if orphan_entities:
            f.write("\n## Orphan Entities (No Device, No Area)\n\n")
            for entity in sorted(orphan_entities, key=lambda x: x['id']):
                status = get_entity_status(entity)
                f.write(f"- Entity: `{entity['id']}` ({entity['name']}){status}\n")

if __name__ == "__main__":
    main()
