""" display and update data from sqlite db in a kivy RecycleView """
import sqlite3

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.button import Button
from kivy.properties import BooleanProperty, ListProperty, StringProperty, ObjectProperty, NumericProperty
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.popup import Popup


connection = sqlite3.connect("demo.db")
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS Callbacks(cID INT, cName TEXT, cbTime INT, cbRems TEXT)")
cursor.execute("SELECT * FROM Callbacks")
loaded_db_rows = cursor.fetchall()
if not loaded_db_rows:
    cursor.execute("INSERT INTO Callbacks VALUES ('1','Client1','1500','Test1')")
    cursor.execute("INSERT INTO Callbacks VALUES ('2','Client2','1600','Test2')")
    cursor.execute("INSERT INTO Callbacks VALUES ('3','Client3','1700','Test3')")
    connection.commit()
cursor.execute("SELECT ROWID, * FROM Callbacks ORDER BY ROWID DESC")
loaded_db_rows = cursor.fetchall()


class TextInputPopup(Popup):
    """ Edit name popup """
    obj = ObjectProperty()
    obj_text = StringProperty()
    obj_id = NumericProperty()

    def __init__(self, obj, **kwargs):
        super(TextInputPopup, self).__init__(**kwargs)
        self.obj = obj
        self.obj_text = obj.text
        print(f"TextInputPopup data index {obj.index}")


class SelectableRecycleGridLayout(FocusBehavior, LayoutSelectionBehavior,
                                  RecycleGridLayout):
    """ Adds selection and focus behaviour to the view. """


class SelectableButton(RecycleDataViewBehavior, Button):
    """ Add selection support to the Button """
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty()
    r_v = None

    def refresh_view_attrs(self, rv, index, data):
        """ Catch and handle the view changes """
        self.index = index
        self.r_v = rv
        return super(SelectableButton, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        """ Add selection on touch down """
        if super(SelectableButton, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        """ Respond to the selection of items in the view. """
        self.selected = is_selected

    def on_press(self):
        """ user pressed edit button """
        popup = TextInputPopup(self)
        popup.open()

    def update_changes(self, idx, txt):
        """ update user changes from popup in grid and db """
        self.text = txt
        grid_row = int(idx / 5)
        grid_col = idx % 5
        rv_data = self.r_v.data
        assert rv_data[idx]['row_id'] == grid_row
        assert rv_data[idx]['col_id'] == grid_col

        db_id = rv_data[grid_row * 5]['text']
        col_name = ['ROWID', 'cID', 'cName', 'cbTime', 'cbRems'][grid_col]
        # noinspection SqlInjection
        cursor.execute(f"UPDATE Callbacks SET {col_name} = '{txt}' WHERE ROWID = {db_id}")
        connection.commit()
        print(f"Changed {col_name} value to '{txt}' in grid_row=={grid_row} with db ROWID of {db_id}")


class RV(BoxLayout):
    """ RecycleView"""
    data_items = ListProperty([])

    def __init__(self, **kwargs):
        """ init RV """
        super(RV, self).__init__(**kwargs)
        self.get_users()

    def get_users(self):
        """ load user data into data_items attribute """

        for row in loaded_db_rows:
            for col in row:
                self.data_items.append(col)

        print("data_items ROWS")
        for row_num in range(len(loaded_db_rows)):
            print(self.data_items[row_num * 5: row_num * 5 + 5])
        print("RecycleView data")
        rv = self.ids.rec_view
        for col_num, col_data in enumerate(rv.data):
            print(f"{col_num}: {col_data}")


class TestApp(App):
    """ main app """
    title = "Kivy RecycleView & SQLite3 Demo"
    kv_file = 'db_grid.kv'

    def build(self):
        """ build kivy widgets """
        return RV()


if __name__ == "__main__":
    TestApp().run()
