from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction

from py.tools import *




class CustomExtension(Extension):

    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())  


def get_event_id(event, extension):
    # find keyword based on id
    for id, kw in extension.preferences.items():
      if kw == event.get_keyword():
        return id
    return ""

class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        print("======================\KeyboardQueryEvent\n======================")
        # multiple keywords options
        match get_event_id(event, extension):
            case "action": return RenderResultListAction(gen_list_custom_actions())
        return HideWindowAction()

class ItemEnterEventListener(EventListener):

    def on_event(self, event, extension):
        # event is instance of ItemEnterEvent

        # turn string into json dict
        action : dict = json.loads(event.get_data())
        
        print("======================\nItemEnterEvent\n======================")

        items = []
        match action["action-type"]:
            case "group": items = gen_list_custom_actions(action['group']['path'])
            case "multi": items = gen_list_custom_actions(actions_list=action['multi'])
            case other: return HideWindowAction()

        # you may want to return another list of results
        return RenderResultListAction(items)


if __name__ == '__main__':
    CustomExtension().run()
