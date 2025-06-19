from mesa.visualization.modules import CanvasGrid, ChartModule

def agent_portrayal(agent):
    color = "gray"
    radius = 0.6
    layer = 0

    if agent.type == "house":
        color = "brown"
        radius = 0.4
        layer = 0
    elif agent.action == "prepare":
        color = "cyan"
    elif agent.action == "partial_prepare":
        color = "lightblue"
    elif agent.action == "mitigate":
        color = "blue"
    elif agent.action == "evacuate":
        color = "red"
    elif agent.action == "shelter_in_place":
        color = "orange"
    elif agent.action == "relocate":
        color = "purple"
    elif agent.action == "recover":
        color = "green"
    elif agent.action == "depend_on_aid":
        color = "yellow"
    elif agent.action == "fatality":
        color = "black"
        radius = 1.0
    elif agent.action == "do_nothing" or agent.action is None:
        color = "gray"

    portrayal = {
        "Shape": "circle",
        "Filled": "true",
        "r": radius,
        "Color": color,
        "Layer": layer
    }
    return portrayal

def get_canvas_grid(width=10, height=10):
    return CanvasGrid(agent_portrayal, width, height, 500, 500)

def get_chart_module():
    return ChartModule([
        {"Label": "prepare", "Color": "cyan"},
        {"Label": "partial_prepare", "Color": "lightblue"},
        {"Label": "mitigate", "Color": "blue"},
        {"Label": "evacuate", "Color": "red"},
        {"Label": "shelter_in_place", "Color": "orange"},
        {"Label": "relocate", "Color": "purple"},
        {"Label": "recover", "Color": "green"},
        {"Label": "depend_on_aid", "Color": "yellow"},
        {"Label": "fatality", "Color": "black"}
    ])
