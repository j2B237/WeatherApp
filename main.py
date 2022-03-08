import json
from kivy.app import App
from kivy.network.urlrequest import UrlRequest
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.properties import BooleanProperty, StringProperty, ObjectProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    """ Adds selection and focus behaviour to the view """


class SelectableLabel(RecycleDataViewBehavior, Label):
    """ Add selection support to the Label """
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        """ Catch and handle the view changes """
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        """ Add selection on touch down"""
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        """ Respond to the selection of items in the view."""
        self.selected = is_selected
        if is_selected:
            print("selection changed to {0}".format(rv.data[index]))
        else:
            print("selection removed for {0}".format(rv.data[index]))


class WeatherRoot(BoxLayout):
    pass


class AddLocationForm(BoxLayout):
    """ Class for adding location """
    api_key = "a897226eca88a4ca4858a9847600b164"
    search_input = ObjectProperty()

    def __init__(self, **kwargs):
        super(AddLocationForm, self).__init__(**kwargs)

    def on_search_btn_pressed(self):
        """ Search for location forecast """
        data = []
        url_template = "http://api.openweathermap.org/data/2.5/find?q={}&appid={}&lang=fr"
        search_url = url_template.format(self.search_input.text, self.api_key)
        request = UrlRequest(search_url, on_success=self.found_location, on_failure=self.on_weather_request_failed(data))

    def on_location_btn_pressed(self):
        """ search for location forecast based on gps coordinates """
        data = []
        try:
            lat, lon = self.search_input.text.split(',')
            # Display a message even if there are no results
            if lat or lon is None:
                self.ids.search_results_list.refreshView(['0 results found'])
            url_template = "http://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}"
            search_url = url_template.format(lat, lon, self.api_key)
            request = UrlRequest(search_url, on_success=self.found_coordinates,
                                 on_failure=self.on_weather_request_failed(data))
        except Exception as e:
            self.ids.search_results_list.refreshView(['0 results found'])
            print(e)

    def found_location(self, request, data):
        """ Get location weather infos by its name """
        data = json.loads(data.decode()) if not isinstance(data, dict) else data
        try:
            results = ["{} ({})".format(d['name'], d['sys']['country']) for d in data['list']]
            self.ids.search_results_list.refreshView(results)
        except Exception as e:
            self.ids.search_results_list.refreshView(['0 results found'])
            print(e)

    def found_coordinates(self, request, data):
        """ Get place weather infos by its coordinates """
        data = json.loads(data.decode()) if not isinstance(data, dict) else data
        try:
            results = {"{} ({})".format(data['name'], data['sys']['country'])}
            self.ids.search_results_list.refreshView(results)
        except Exception as e:
            self.ids.search_results_list.refreshView(['0 results found'])
            print(e)

    def on_weather_request_failed(self, data):
        if len(data) == 0:
            self.ids.search_results_list.refreshView(['0 results found'])


class RV(RecycleView):
    # suggested_location = ["Palo Alto, MX", "Palo Alto, US"]

    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        # self.data = [{"text": str(d)} for d in self.suggested_location]

    def refreshView(self, locations):
        self.data = [{"text": str(d)} for d in locations]


class WeatherApp(App):

    def build(self):
        return WeatherRoot()


if __name__ == "__main__":
    WeatherApp().run()



