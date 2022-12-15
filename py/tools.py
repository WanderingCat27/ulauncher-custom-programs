from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from ulauncher.api.shared.action.OpenAction import OpenAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
import requests

from os import scandir
from os.path import exists

import json
from py.consts import *

def get_custom_actions_data(dir):
    # read all json files in custom folder
    list = []
    with scandir(dir) as folder: 
        for f in folder:
            if f.name.endswith(".json") and f.is_file() and f.name != "group.json": 
                try_save_url(f.path)
                list.append(json_file_to_dict(f))
            # if found folder, append a group
            if f.is_dir(): 
                group = {
                    "name": f.name,
                    "description": "create a group.json file to edit properties of this group",
                    "icon": FOLDER_ICON,
                    "action-type": "group",
                    "group": {
                        "path": f.path
                    }
                }
                #check if f contains a group.json file
                if exists(f.path + "/group.json"):
                    data = json_file_to_dict(f.path + "/group.json")
                    group["name"] = data["name"]
                    group["description"] = data["description"]
                    if "icon" in data:
                        group["icon"] = data["icon"]
                list.append(group)

    # return list of dicts
    return list


def gen_list_custom_actions(dir=ACTIONS_FOLDER, actions_list=None):
    if actions_list == None: actions_list=get_custom_actions_data(dir)
    items = []

    for ac in actions_list:
        icon_path = EXTENSION_ICON_FILE
        # check if icon is defined
        if 'icon' in ac:
            icon_path=replace_ICON_FILE(ac['icon'])
        
        items.append(ExtensionResultItem(
            icon=icon_path,
            name=ac["name"],
            description=ac["description"],
            on_enter=process_action(ac)
        ))
    return items

def process_action(action):
    match action['action-type']:
        case "open_url": return OpenUrlAction(action["open_url"]["url"])
        case "open_file": return OpenAction(replace_WORKING_DIR(action["open_file"]["path"]))
        case "script": return RunScriptAction(replace_WORKING_DIR(action["script"]["path"]))
        # custom actions
        case "group" | "multi": return ExtensionCustomAction(json.dumps(action), keep_app_open=True)
        case other: return DoNothingAction() # could change to an action that says invalid action-type

def json_file_to_dict(path):
    # read json file and return dict
    with open(path) as json_file:
        return json.load(json_file)

def replace_WORKING_DIR(p):
    return p.replace("%WDIR/", WORKING_DIR).replace("%WDIR", WORKING_DIR)
def replace_ICON_FILE(p):
    return p.replace("%ICON/", ICON_DIR).replace("%ICONS/", ICON_DIR).replace("%ICON", ICON_DIR).replace("%ICONS", ICON_DIR)



# function that takes a url to an image as an input and saves it to the icon folder and returns the path to the icon
def try_save_url(action_file_loc):
    dict = json_file_to_dict(action_file_loc)
    if 'icon' not in dict or not dict['icon'].startswith("http"):
        return
    if not exists(ICON_DIR + "downloaded/"):
        print("DOWNLOAD FOLDER DOES NOT EXIST")
        return

    # try to save the image
    url = dict['icon']
    # turn a url into a file name
    file_name = url.split("/")[-1]   

    file_loc = ICON_DIR + "downloaded/" +file_name
    # try to download image from url
    try:
        r = requests.get(url, allow_redirects=True)
    except:
        print("ERROR DOWNLOADING ICON")
        return

    # save the file
    with open(file_loc, 'wb') as f:
        f.write(r.content)
    print(file_loc)

    data = ""
    with open(action_file_loc, 'r') as f:
        data = f.read().replace(url, "%ICONS/downloaded/" + file_name)
    # write the new data to the file
    with open(action_file_loc, 'w') as f:
        f.write(data)
