import os
import re
import json
import uuid
import zipfile
from datetime import datetime

# Function to parse the markdown file


def parse_markdown(md_file):
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract all group sections
    groups = {}

    # Regular expression to find group sections
    group_sections = re.findall(
        r'## ([^\n]+)\n\n(.*?)(?=\n## |$)', content, re.DOTALL)

    for group_name, group_content in group_sections:
        # Extract color from the first table row
        color_match = re.search(r'\|(.*?)\|(.*?)\|(.*?)\|', group_content)
        group_color = None
        if color_match:
            # Try to find the group color in the table
            color_lines = re.findall(r'\|[^|]*\|[^|]*\|(.*?)\|', group_content)
            if color_lines and len(color_lines) > 1:  # Skip header row
                group_color = color_lines[1].strip()

        # Extract shortcuts from tables
        shortcuts = []

        # Find all table rows
        table_rows = re.findall(
            r'\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|', group_content)

        # Skip header row and separator row
        for row in table_rows[2:]:  # Skip header and separator rows
            action = row[0].strip()
            shortcut = row[1].strip()
            color = row[2].strip()
            icon = row[3].strip()
            color_override = row[4].strip()
            notes = row[5].strip()

            # Skip empty rows or rows with empty shortcuts
            if not action or not shortcut or shortcut == '(none – use mouse click)':
                continue

            shortcuts.append({
                'action': action,
                'shortcut': shortcut,
                'color': color,
                'icon': icon,
                'color_override': color_override,
                'notes': notes
            })

        # Create the group entry
        groups[group_name] = {
            'color': group_color,
            'shortcuts': shortcuts
        }

    return groups

# Function to generate a UUID-based name (similar to Loupedeck's naming)


def generate_id():
    return str(uuid.uuid4()).replace('-', '').upper()

# Function to convert shortcut string to Loupedeck format


def convert_shortcut(shortcut_str):
    # Map shortcut keys to Loupedeck's format
    key_mapping = {
        'Ctrl': 'ControlOrCommand',
        'Cmd': 'ControlOrCommand',
        'Alt': 'AltOrOption',
        'Opt': 'AltOrOption',
        'Shift': 'Shift',
        'Enter': 'Enter',
        'Space': 'Space',
        'Backspace': 'Backspace',
        'Tab': 'Tab',
        'Esc': 'Escape',
        'Del': 'Delete',
        'Ins': 'Insert',
        'Home': 'Home',
        'End': 'End',
        'PgUp': 'PageUp',
        'PgDown': 'PageDown',
        'F1': 'F1', 'F2': 'F2', 'F3': 'F3', 'F4': 'F4', 'F5': 'F5',
        'F6': 'F6', 'F7': 'F7', 'F8': 'F8', 'F9': 'F9', 'F10': 'F10',
        'F11': 'F11', 'F12': 'F12',
        '↑': 'ArrowUp', '↓': 'ArrowDown', '←': 'ArrowLeft', '→': 'ArrowRight',
        'Up': 'ArrowUp', 'Down': 'ArrowDown', 'Left': 'ArrowLeft', 'Right': 'ArrowRight',
        'ArrowUp': 'ArrowUp', 'ArrowDown': 'ArrowDown', 'ArrowLeft': 'ArrowLeft', 'ArrowRight': 'ArrowRight'
    }

    # Extract basic parts of the shortcut
    parts = shortcut_str.replace('/', '').split('+')
    processed_parts = []

    # Process each part to match Loupedeck's format
    for part in parts:
        part = part.strip()
        if part in key_mapping:
            processed_parts.append(key_mapping[part])
        elif len(part) == 1 and part.isalpha():
            processed_parts.append(f"Key{part.upper()}")
        elif part.startswith('NumPad'):
            processed_parts.append(part)
        else:
            # For other keys, just use as is
            processed_parts.append(part)

    # Join the processed parts with the appropriate separator
    loupedeck_shortcut = '+'.join(processed_parts)

    # Define virtual key codes mapping (Windows)
    virtual_key_codes = {
        'KeyA': 'win-65', 'KeyB': 'win-66', 'KeyC': 'win-67', 'KeyD': 'win-68', 'KeyE': 'win-69',
        'KeyF': 'win-70', 'KeyG': 'win-71', 'KeyH': 'win-72', 'KeyI': 'win-73', 'KeyJ': 'win-74',
        'KeyK': 'win-75', 'KeyL': 'win-76', 'KeyM': 'win-77', 'KeyN': 'win-78', 'KeyO': 'win-79',
        'KeyP': 'win-80', 'KeyQ': 'win-81', 'KeyR': 'win-82', 'KeyS': 'win-83', 'KeyT': 'win-84',
        'KeyU': 'win-85', 'KeyV': 'win-86', 'KeyW': 'win-87', 'KeyX': 'win-88', 'KeyY': 'win-89',
        'KeyZ': 'win-90',
        'ArrowLeft': 'win-37', 'ArrowUp': 'win-38', 'ArrowRight': 'win-39', 'ArrowDown': 'win-40',
        'F1': 'win-112', 'F2': 'win-113', 'F3': 'win-114', 'F4': 'win-115', 'F5': 'win-116',
        'F6': 'win-117', 'F7': 'win-118', 'F8': 'win-119', 'F9': 'win-120', 'F10': 'win-121',
        'F11': 'win-122', 'F12': 'win-123',
        'Enter': 'win-13', 'Space': 'win-32', 'Escape': 'win-27', 'Tab': 'win-9',
        'Backspace': 'win-8', 'Delete': 'win-46', 'Insert': 'win-45',
        'Home': 'win-36', 'End': 'win-35', 'PageUp': 'win-33', 'PageDown': 'win-34',
        'NumPad0': 'win-96', 'NumPad1': 'win-97', 'NumPad2': 'win-98', 'NumPad3': 'win-99',
        'NumPad4': 'win-100', 'NumPad5': 'win-101', 'NumPad6': 'win-102', 'NumPad7': 'win-103',
        'NumPad8': 'win-104', 'NumPad9': 'win-105',
        'Multiply': 'win-106', 'Add': 'win-107', 'Subtract': 'win-109', 'Decimal': 'win-110', 'Divide': 'win-111',
    }

    # Add specific formatting for Loupedeck
    key_id = "67699721"  # Default ID used in the reference
    formatted_shortcut = f"{loupedeck_shortcut}___{key_id}___{shortcut_str}___"

    # Add virtual key code if available
    vk_added = False
    for part in processed_parts:
        if part in virtual_key_codes:
            formatted_shortcut += virtual_key_codes[part]
            vk_added = True
            break

    # If no specific virtual key was found, try to get one from the last part
    if not vk_added and processed_parts:
        last_part = processed_parts[-1]
        # Handle NumPad keys specially
        if last_part.startswith('NumPad'):
            num = last_part[6:]
            if num.isdigit() and 0 <= int(num) <= 9:
                formatted_shortcut += f"win-{96 + int(num)}"
                vk_added = True

    # Calculate modifier flag value
    modifier_value = 0
    if "ControlOrCommand" in formatted_shortcut:
        modifier_value += 128
    if "Shift" in formatted_shortcut:
        modifier_value += 64
    if "AltOrOption" in formatted_shortcut:
        modifier_value += 2

    # Add modifier flag if any modifier is present
    if modifier_value > 0:
        formatted_shortcut += f"#¤%&+?{modifier_value}"

    # Add the key ID and closing part
    formatted_shortcut += f"#¤%&+?{key_id}#¤%&+?44"

    return formatted_shortcut

# Function to create an action


def create_action(action_name, shortcut, group_name):
    action_id = f"$@Generic___@ProfileAction___{generate_id()}"

    action = {
        "$type": "Loupedeck.Service.ApplicationProfileCommand, LoupedeckService",
        "isCommand": True,
        "name": action_id,
        "templateActionName": "$@Generic___@KeyboardKey",
        "actionParameters": {
            "$type": "Loupedeck.ActionEditorActionParameters, PluginApi",
            "parameters": {
                "$type": "Loupedeck.StringDictionaryNoCase, PluginApi",
                "keyboardKey": convert_shortcut(shortcut)
            },
            "count": 1
        },
        "displayName": action_name,
        "description": "Activate a keyboard shortcut with a single press or hold down for continuous use like a keyboard key",
        "groupName": group_name,
        "superGroupName": "@macro",
        "isProfileAction": True,
        "isMultiState": False,
        "isResetCommand": False,
        "adjustmentName": None,
        "states": None
    }

    return action_id, action

# Function to create a default icon file


def create_default_icon(action_id, display_name):
    # Base icon content from the reference files
    icon_content = {
        "backgroundColor": 4278190080,
        "items": [
            {
                "$type": "Loupedeck.Service.ActionIconImageItem, LoupedeckShared",
                "image": "PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4NCjxwYXRoIGZpbGwtcnVsZT0iZXZlbm9kZCIgY2xpcC1ydWxlPSJldmVub2RkIiBkPSJNMjAgMTNDMTYuNjg2MyAxMyAxNCAxNS42ODYzIDE0IDE5QzE0IDIyLjMxMzcgMTYuNjg2MyAyNSAyMCAyNUMyMy4zMTM3IDI1IDI2IDIyLjMxMzcgMjYgMTlDMjYgMTUuNjg2MyAyMy4zMTM3IDEzIDIwIDEzWk0xMiAxOUMxMiAxNC41ODE3IDE1LjU4MTcgMTEgMjAgMTFDMjQuNDE4MyAxMSAyOCAxNC41ODE3IDI4IDE5QzI4IDIzLjQxODMgMjQuNDE4MyAyNyAyMCAyN0MxNS41ODE3IDI3IDEyIDIzLjQxODMgMTIgMTlaIiBmaWxsPSIjRTJFMkUyIi8+DQo8cGF0aCBmaWxsLXJ1bGU9ImV2ZW5vZGQiIGNsaXAtcnVsZT0iZXZlbm9kZCIgZD0iTTUgOEM1IDYuMzQzMTUgNi4zNDMxNSA1IDggNUgxN0MxNy41NTIzIDUgMTggNS40NDc3MiAxOCA2QzE4IDYuNTUyMjggMTcuNTUyMyA3IDE3IDdIOEM3LjQ0NzcyIDcgNyA3LjQ0NzcyIDcgOFYxNkM3IDE2LjU1MjMgNy40NDc3MiAxNyA4IDE3SDlDOS41NTIyOCAxNyAxMCAxNy40NDc3IDEwIDE4QzEwIDE4LjU1MjMgOS41NTIyOCAxOSA5IDE5SDhDNi4zNDMxNSAxOSA1IDE3LjY1NjkgNSAxNlY4WiIgZmlsbD0iI0UyRTJFMiIvPg0KPHBhdGggZmlsbC1ydWxlPSJldmVub2RkIiBjbGlwLXJ1bGU9ImV2ZW5vZGQiIGQ9Ik05IDE0QzkgMTMuNDQ3NyA5LjQ0NzcyIDEzIDEwIDEzQzEwLjU1MjMgMTMgMTEuMDAwMSAxMy40NDc3IDExLjAwMDEgMTRDMTEuMDAwMSAxNC41NTIzIDEwLjU1MjQgMTUgMTAuMDAwMSAxNUM5LjQ0NzgyIDE1IDkgMTQuNTUyMyA5IDE0WiIgZmlsbD0iI0UyRTJFMiIvPg0KPHBhdGggZmlsbC1ydWxlPSJldmVub2RkIiBjbGlwLXJ1bGU9ImV2ZW5vZGQiIGQ9Ik05IDEwQzkgOS40NDc3MiA5LjQ0NzcyIDkgMTAgOUMxMC41NTIzIDkgMTEuMDAwMSA5LjQ0NzcyIDExLjAwMDEgMTBDMTEuMDAwMSAxMC41NTIzIDEwLjU1MjQgMTEgMTAuMDAwMSAxMUM5LjQ0NzgyIDExIDkgMTAuNTUyMyA5IDEwWiIgZmlsbD0iI0UyRTJFMiIvPg0KPHBhdGggZmlsbC1ydWxlPSJldmVub2RkIiBjbGlwLXJ1bGU9ImV2ZW5vZGQiIGQ9Ik0xMyAxMEMxMyA5LjQ0NzcyIDEzLjQ0NzcgOSAxNCA5QzE0LjU1MjMgOSAxNS4wMDAxIDkuNDQ3NzIgMTUuMDAwMSAxMEMxNS4wMDAxIDEwLjU1MjMgMTQuNTUyNCAxMSAxNC4wMDAxIDExQzEzLjQ0NzggMTEgMTMgMTAuNTUyMyAxMyAxMFoiIGZpbGw9IiNFMkUyRTIiLz4NCjwvc3ZnPg0K",
                "imageFileName": "",
                "imageColor": 4294967295,
                "imageRotation": "None",
                "isVisible": True,
                "itemType": "Image",
                "area": {
                    "x": 9,
                    "y": 0,
                    "width": 82,
                    "height": 82,
                    "isFullScreen": False
                }
            },
            {
                "$type": "Loupedeck.Service.ActionIconTextItem, LoupedeckShared",
                "text": display_name,
                "textColor": 4294967295,
                "fontSize": 4,
                "fontName": "Arial",
                "isVisible": True,
                "itemType": "Text",
                "area": {
                    "x": 0,
                    "y": 66,
                    "width": 100,
                    "height": 34,
                    "isFullScreen": False
                }
            }
        ]
    }

    # Adjust text y position based on text length
    if len(display_name) <= 10:
        icon_content["items"][1]["area"]["y"] = 81
        icon_content["items"][1]["area"]["height"] = 18

    return json.dumps(icon_content, indent=2)

# Function to create a group


def create_group(group_name):
    group_id = generate_id()
    group = {
        "$type": "Loupedeck.Service.ApplicationProfileMacroCommand, LoupedeckService",
        "isCommand": True,
        "name": group_id,
        "displayName": "___GROUP___",
        "description": "",
        "groupName": group_name,
        "superGroupName": "@macro",
        "supportedOs": "All",
        "supportedModes": [
            "main"
        ],
        "showAsSingleAction": False,
        "actionEditorCommands": [],
        "isMultiState": False,
        "actions": []
    }

    return group_id, group

# Function to create the profile structure


def create_profile_structure(groups_data):
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    profile_id = "1FB101FDAB5541C0973D10A891A60B36"  # Using same ID as reference

    # Create application info
    app_info = {
        "$type": "Loupedeck.Service.SupportedApplicationInfo, LoupedeckService",
        "name": "fl64",
        "displayName": "FL Studio 2024",
        "description": None,
        "deviceType": "Loupedeck30",
        "nativePluginName": None,
        "hasNativePlugin": False,
        "processOrBundleName": "fl64",
        "modes": [
            {
                "$type": "Loupedeck.Service.ApplicationMode, LoupedeckService",
                "name": "main",
                "parentModeName": None,
                "displayName": "Main"
            }
        ],
        "defaultProfileName": profile_id,
        "isEnabled": True
    }

    # Create profile structure
    profile = {
        "$type": "Loupedeck.Service.ApplicationProfile, LoupedeckService",
        "name": profile_id,
        "profileFlags": "None",
        "displayName": "FL Studio Controls",
        "description": None,
        "deviceType": "Loupedeck30",
        "applicationName": "fl64",
        "nativePluginName": None,
        "hasNativePlugin": False,
        "additionalNativePluginNames": [
            "ObsStudio",
            "Twitch",
            "DefaultWin"
        ],
        "lastModifiedTimeUtc": now,
        "profileSettings": {
            "$type": "Loupedeck.DictionaryNoCase`1[[System.String, System.Private.CoreLib]], PluginApi"
        },
        "actionImages90": None,
        "actionImages60": None,
        "wheelImages": None,
        "actionColors": None,
        "layout": create_default_layout(),
        "macroCommands": [],
        "macroAdjustments": [],
        "profileCommands": [],
        "profileAdjustments": [],
        "conversionHistory": f"{now} aa 6.1.0.22061\r\n{now} ab 6.1.0.22061\r\n",
        "packageName": None,
        "packageVersion": None,
        "profileActions": []
    }

    # Create metadata files
    advanced_info = {
        "additionalPluginNames": []
    }

    package_yaml = f"""type: Profile5
name: {profile_id}
displayName: FL Studio Controls
version: 1.0.0
"""

    profile_preview = {
        "buttonPages": [None] * 15,
        "encoderPages": [None] * 6
    }

    # Add groups and actions
    for group_name, group_data in groups_data.items():
        group_id, group_obj = create_group(group_name)
        profile["macroCommands"].append(group_obj)

        for shortcut in group_data["shortcuts"]:
            action_id, action_obj = create_action(
                shortcut["action"], shortcut["shortcut"], group_name)
            profile["profileActions"].append(action_obj)

    return app_info, profile, advanced_info, package_yaml, profile_preview

# Function to create a default layout


def create_default_layout():
    return {
        "$type": "Loupedeck.Service.ProfileLayout20, LoupedeckService",
        "deviceType": "Loupedeck30",
        "profileFlags": "None",
        "layoutModes": [
            {
                "$type": "Loupedeck.Service.ProfileLayoutMode20, LoupedeckService",
                "deviceType": "Loupedeck30",
                "modeName": "main",
                "parentModeName": None,
                "actions": None,
                "dynamicButtonPages": None,
                "dynamicEncoderPages": None,
                "touchPages": [
                    {
                        "$type": "Loupedeck.Service.ProfileLayoutButtonPage, LoupedeckService",
                        "name": generate_id(),
                        "displayName": "Touch Page (1)",
                        "description": None,
                        "controls": [
                            {
                                "$type": "Loupedeck.Service.ProfileLayoutButton, LoupedeckService",
                                "pressAction": None,
                                "fnPressAction": None
                            }
                        ] * 15,
                        "dynamicPageName": None,
                        "dynamicPagePluginName": None,
                        "dynamicPageNumber": 0
                    }
                ],
                "encoderPages": [
                    {
                        "$type": "Loupedeck.Service.ProfileLayoutEncoderPage, LoupedeckService",
                        "name": generate_id(),
                        "displayName": "Dial Page (1)",
                        "description": None,
                        "controls": [
                            {
                                "$type": "Loupedeck.Service.ProfileLayoutEncoder, LoupedeckService",
                                "pressAction": None,
                                "fnPressAction": None,
                                "rotateAction": None,
                                "fnRotateAction": None
                            }
                        ] * 6,
                        "dynamicPageName": None,
                        "dynamicPagePluginName": None,
                        "dynamicPageNumber": 0
                    }
                ],
                "wheelPages": [
                    {
                        "$type": "Loupedeck.Service.ProfileLayoutWheelPage, LoupedeckService",
                        "name": generate_id(),
                        "displayName": "Clock",
                        "description": None,
                        "templateName": "WheelToolAnalogClock",
                        "parameters": {
                            "$type": "Loupedeck.StringDictionaryNoCase, PluginApi",
                            "actions": "$@Generic___@ButtonClock",
                            "adjustment": "$@Generic___@MouseWheel"
                        }
                    }
                ],
                "workspaces": [
                    {
                        "$type": "Loupedeck.Service.ProfileLayoutWorkspace20, LoupedeckService",
                        "name": generate_id(),
                        "displayName": "Workspace (1)",
                        "description": None,
                        "touchPageNames": [
                            "$touchPageId"  # To be replaced later
                        ],
                        "encoderPageNames": [
                            "$encoderPageId"  # To be replaced later
                        ],
                        "wheelPageNames": [
                            "$wheelPageId"  # To be replaced later
                        ],
                        "activationActions": []
                    }
                ],
                "homeWorkspaceName": "$workspaceId"  # To be replaced later
            }
        ],
        "roundPage": {
            "$type": "Loupedeck.Service.ProfileLayoutButtonPage, LoupedeckService",
            "name": generate_id(),
            "displayName": "",
            "description": None,
            "controls": [
                {
                    "$type": "Loupedeck.Service.ProfileLayoutButton, LoupedeckService",
                    "pressAction": None,
                    "fnPressAction": None
                }
            ] * 8,
            "dynamicPageName": None,
            "dynamicPagePluginName": None,
            "dynamicPageNumber": 0
        },
        "squarePage": {
            "$type": "Loupedeck.Service.ProfileLayoutButtonPage, LoupedeckService",
            "name": generate_id(),
            "displayName": "",
            "description": None,
            "controls": [
                {
                    "$type": "Loupedeck.Service.ProfileLayoutButton, LoupedeckService",
                    "pressAction": None,
                    "fnPressAction": None
                }
            ] * 12,
            "dynamicPageName": None,
            "dynamicPagePluginName": None,
            "dynamicPageNumber": 0
        }
    }

# Function to create a .lp5 file from the profile directory


def create_lp5_file(source_dir, output_lp5):
    """
    Create a Loupedeck .lp5 file from the generated profile directory.

    Args:
        source_dir: Directory containing the generated profile files
        output_lp5: Path for the output .lp5 file
    """
    with zipfile.ZipFile(output_lp5, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Walk through the directory
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                # Get the full file path
                file_path = os.path.join(root, file)
                # Calculate the archive path (relative to source_dir)
                arcname = os.path.relpath(file_path, source_dir)
                # Add the file to the zip
                zipf.write(file_path, arcname)

    print(f"Successfully created Loupedeck profile: {output_lp5}")

# Main function to generate the profile


def generate_profile(md_file, output_dir, output_lp5=None):
    # Parse the markdown file
    groups_data = parse_markdown(md_file)

    # Create output directory structure
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'metadata'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'ActionIcons'), exist_ok=True)

    # Create profile structure
    app_info, profile, advanced_info, package_yaml, profile_preview = create_profile_structure(
        groups_data)

    # Fix IDs in layout
    touch_page_id = profile["layout"]["layoutModes"][0]["touchPages"][0]["name"]
    encoder_page_id = profile["layout"]["layoutModes"][0]["encoderPages"][0]["name"]
    wheel_page_id = profile["layout"]["layoutModes"][0]["wheelPages"][0]["name"]
    workspace_id = profile["layout"]["layoutModes"][0]["workspaces"][0]["name"]

    profile["layout"]["layoutModes"][0]["workspaces"][0]["touchPageNames"] = [
        touch_page_id]
    profile["layout"]["layoutModes"][0]["workspaces"][0]["encoderPageNames"] = [
        encoder_page_id]
    profile["layout"]["layoutModes"][0]["workspaces"][0]["wheelPageNames"] = [
        wheel_page_id]
    profile["layout"]["layoutModes"][0]["homeWorkspaceName"] = workspace_id

    # Save all the files
    with open(os.path.join(output_dir, 'ApplicationInfo.json'), 'w', encoding='utf-8') as f:
        json.dump(app_info, f, indent=2)

    with open(os.path.join(output_dir, 'ProfileInfo.json'), 'w', encoding='utf-8') as f:
        json.dump(profile, f, indent=2)

    with open(os.path.join(output_dir, 'metadata', 'AdvancedInfo.json'), 'w', encoding='utf-8') as f:
        json.dump(advanced_info, f, indent=2)

    with open(os.path.join(output_dir, 'metadata', 'LoupedeckPackage.yaml'), 'w', encoding='utf-8') as f:
        f.write(package_yaml)

    with open(os.path.join(output_dir, 'metadata', 'ProfilePreview.json'), 'w', encoding='utf-8') as f:
        json.dump(profile_preview, f, indent=2)

    # Create icon files for each action
    for action in profile["profileActions"]:
        action_id = action["name"]
        display_name = action["displayName"]
        icon_file_path = os.path.join(
            output_dir, 'ActionIcons', f'{action_id}.ict')
        with open(icon_file_path, 'w', encoding='utf-8') as f:
            f.write(create_default_icon(action_id, display_name))

    print(f"Profile generated successfully in '{output_dir}'")
    print(f"Total groups created: {len(profile['macroCommands'])}")
    print(f"Total actions created: {len(profile['profileActions'])}")

    # Create .lp5 file if requested
    if output_lp5:
        create_lp5_file(output_dir, output_lp5)

    return profile


# Usage example
if __name__ == "__main__":
    # Get the current directory
    current_dir = os.getcwd()

    # Input and output paths
    md_file = os.path.join(current_dir, "FL Studio Controls.md")
    output_dir = os.path.join(current_dir, "FL_Studio_Loupedeck_Profile")
    output_lp5 = os.path.join(current_dir, "FL_Studio_Controls.lp5")

    # Generate the profile
    profile = generate_profile(md_file, output_dir, output_lp5)

    print("Profile generation complete!")
    print(f"Profile saved to: {output_dir}")
    print(f"Loupedeck .lp5 file saved to: {output_lp5}")
