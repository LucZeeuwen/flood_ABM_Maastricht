import solara
from solara.lab import Tab, Tabs  # This is correct module

@solara.component
def Page():
    with Tabs():
        with Tab("Map"):
            solara.Text("This is the Map tab.")
        with Tab("Statistics"):
            solara.Text("This is the Statistics tab.")
