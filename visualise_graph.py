from agents import create_workflow

try:
    graph_image = create_workflow().get_graph().draw_mermaid_png()
    with open("graph.png", "wb") as f:
        f.write(graph_image)
    print("Graph saved as graph.png")
except Exception as e:
    print(f"An error occurred: {e}")
