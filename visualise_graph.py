from workflow import app

try:
    graph_image = app.get_graph().draw_mermaid_png()
    with open("graph.png", "wb") as f:
        f.write(graph_image)
    print("Graph saved as graph.png")
except Exception as e:
    print(f"An error occurred: {e}")
