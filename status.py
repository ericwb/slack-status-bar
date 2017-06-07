import copy
import json
import os
import signal
import sys
import yaml

from CalendarStore import CalCalendarStore
from CalendarStore import NSDate
import objc
import Quartz
import requests
import rumps


APP_TITLE = 'Slack Status'
AUTO = 'Auto'
IN_MEETING = 'In a Meeting'
COMMUTING = 'Commuting'
OUT_SICK = 'Out Sick'
VACATIONING = 'Vacationing'
WORKING_REMOTELY = 'Working Remotely'
AWAY = 'Away'
DO_NOT_DISTURB = 'Do Not Disturb'
PREFERENCES = 'Preferences'


class SlackStatusBarApp(rumps.App):
    def __init__(self, config):
        super(SlackStatusBarApp, self).__init__(
            APP_TITLE, icon=os.path.join('icons', 'Slack_Icon.png'))
        self.config = config

        menu_items = []
        auto_menu_item = rumps.MenuItem(AUTO)
        auto_menu_item.state = True
        menu_items.append(auto_menu_item)
        menu_items.append(None)

        meeting_menu = rumps.MenuItem(IN_MEETING)
        meeting_menu.icon = os.path.join('icons', 'spiral_calendar_pad.png')
        menu_items.append(meeting_menu)

        commute_menu = rumps.MenuItem(COMMUTING)
        commute_menu.icon = os.path.join('icons', 'bus.png')
        menu_items.append(commute_menu)

        sick_menu = rumps.MenuItem(OUT_SICK)
        sick_menu.icon = os.path.join('icons', 'face_with_thermometer.png')
        menu_items.append(sick_menu)

        vacation_menu = rumps.MenuItem(VACATIONING)
        vacation_menu.icon = os.path.join('icons', 'palm_tree.png')
        menu_items.append(vacation_menu)

        remote_menu = rumps.MenuItem(WORKING_REMOTELY)
        remote_menu.icon = os.path.join('icons', 'house_with_garden.png')
        menu_items.append(remote_menu)

        menu_items.append(None)

        away_menu = rumps.MenuItem(AWAY)
        away_menu.icon = os.path.join('icons', 'large_red_circle.png')
        menu_items.append(away_menu)

        dnd_menu = rumps.MenuItem(DO_NOT_DISTURB)
        menu_items.append(dnd_menu)

        menu_items.append(None)

        pref_menu = rumps.MenuItem(PREFERENCES)
        menu_items.append(pref_menu)

        for menu_item in menu_items:
            self.menu.add(copy.copy(menu_item))

    @rumps.timer(60)
    def _check_status(self, sender):
        # Check if on vacation
        store = CalCalendarStore.defaultCalendarStore()

        for calendar in store.calendars():
            if calendar._.title in self.config['vacation_calendars']:
                pred = CalCalendarStore.eventPredicateWithStartDate_endDate_calendars_(
                    NSDate.date(), NSDate.date(), [calendar])
                event = store.eventsWithPredicate_(pred)
                if event:
                    self.set_vacation(None, event._.title[0])
                    return

        # Check if in a meeting
        for calendar in store.calendars():
            if calendar._.title in self.config['work_calendars']:
                pred = CalCalendarStore.eventPredicateWithStartDate_endDate_calendars_(
                    NSDate.date(), NSDate.date(), [calendar])
                event = store.eventsWithPredicate_(pred)
                if event:
                    self.set_meeting(None, event._.title[0])
                    return

        # Check if working remotely
        for if_name in CWInterface.interfaceNames():
            interface = CWInterface.interfaceWithName_(if_name)
            if interface.ssid() == self.config['work_ssid']:
                self.unset_status(None)
            else:
                self.set_remote(None)
            break

        # Check if screen is locked or asleep
        session = Quartz.CGSessionCopyCurrentDictionary()
        if session and session.get('CGSSessionScreenIsLocked', 0):
            self.set_presence_away(None)
        else:
            self.set_presence_auto(None)

    def _send_slack_status(self, status_text, status_emoji):
        url = 'https://slack.com/api/users.profile.set'
        profile = {'status_text': status_text, 'status_emoji': status_emoji}
        payload = {'token': self.config['token'],
                   'profile': json.dumps(profile)}
        r = requests.get(url, params=payload)
        print(r.text)

    @rumps.clicked(AUTO)
    def set_auto(self, sender):
        sender.state = not sender.state
        if sender.state:
            # Turning auto mode ON
            self.set_presence_auto(sender)

            # Disable all callbacks (grays out menu items)
            for key, menu_item in self.menu.iteritems():
                if key == IN_MEETING:
                    menu_item.set_callback(None)
                elif key == COMMUTING:
                    menu_item.set_callback(None)
                elif key == OUT_SICK:
                    menu_item.set_callback(None)
                elif key == VACATIONING:
                    menu_item.set_callback(None)
                elif key == WORKING_REMOTELY:
                    menu_item.set_callback(None)
                elif key == AWAY:
                    menu_item.set_callback(None)

            # Enable timer
            for timer in rumps.timers():
                timer.start()
        elif not sender.state:
            # Turning auto mode OFF

            # Disable timer
            for timer in rumps.timers():
                timer.stop()

            # Enable all callbacks
            for key, menu_item in self.menu.iteritems():
                if key == IN_MEETING:
                    menu_item.set_callback(self.set_meeting)
                elif key == COMMUTING:
                    menu_item.set_callback(self.set_commute)
                elif key == OUT_SICK:
                    menu_item.set_callback(self.set_sick)
                elif key == VACATIONING:
                    menu_item.set_callback(self.set_vacation)
                elif key == WORKING_REMOTELY:
                    menu_item.set_callback(self.set_remote)
                elif key == AWAY:
                    menu_item.set_callback(self.set_presence_away)

    def unset_status(self, sender):
        self._send_slack_status('', '')

    def set_meeting(self, sender, meeting_title):
        if self.config['meeting_title'] is True:
            status_text = IN_MEETING + ': ' + meeting_title
        else:
            status_text = IN_MEETING
        self._send_slack_status(status_text, ':spiral_calendar_pad:')

    def set_commute(self, sender):
        self._send_slack_status(COMMUTING, ':bus:')

    def set_sick(self, sender):
        self._send_slack_status(OUT_SICK, ':face_with_thermometer:')

    def set_vacation(self, sender, vacation_title):
        if self.config['meeting_title'] is True:
            status_text = VACATIONING + ': ' + vacation_title
        else:
            status_text = VACATIONING
        self._send_slack_status(status_text, ':palm_tree:')

    def set_remote(self, sender):
        self._send_slack_status(WORKING_REMOTELY, ':house_with_garden:')

    def set_presence_auto(self, sender):
        url = 'https://slack.com/api/users.setPresence'
        payload = {'token': self.config['token'], 'presence': 'auto'}
        r = requests.get(url, params=payload)
        print(r.text)

    def set_presence_away(self, sender):
        url = 'https://slack.com/api/users.setPresence'
        payload = {'token': self.config['token'], 'presence': 'away'}
        r = requests.get(url, params=payload)
        print(r.text)

    def set_dnd(self, sender):
        # TODO
        pass

    @rumps.clicked(PREFERENCES)
    def preferences(self, sender):
        default_text = ''
        if 'token' in self.config and self.config['token']:
            default_text = self.config['token']
        pref_window = rumps.Window(message='Enter token:',
                                   default_text=default_text, cancel=True)
        pref_window.icon = os.path.join('icons', 'Slack_Icon.png')
        response = pref_window.run()
        if response.clicked and response.text:
            self.config['token'] = response.text


def _signal_handler(signal, frame):
    rumps.quit_application()


def main():
    # Read the configuration file
    config_file = os.path.join(rumps.application_support(APP_TITLE),
                               'config.yaml')
    with open(config_file, 'r') as conf:
        try:
            config = yaml.safe_load(conf)
        except yaml.YAMLError as exc:
            print(exc)
            return

    # Load the WLAN framework
    objc.loadBundle(
        'CoreWLAN',
        bundle_path='/System/Library/Frameworks/CoreWLAN.framework',
        module_globals=globals())

    # Setup our CTRL+C signal handler
    signal.signal(signal.SIGINT, _signal_handler)

    # Enable debug mode
    rumps.debug_mode(config['debug'])

    # Startup application
    SlackStatusBarApp(config).run()


if __name__ == "__main__":
    sys.exit(main())
