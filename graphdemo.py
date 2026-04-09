from IPython.display import Image, display
from agents.graph import build_graph

def main():
    # 1. Build and compile the graph
    graph = build_graph()
    
    # 2. Exact code pattern for visualization
    try:
        print("Attempting to generate graph visualization...")
        # This will render the image in IPython/Jupyter environments
        display(Image(graph.get_graph().draw_mermaid_png()))
        
        # Also saving a copy just in case you want to view it manually
        with open("graph.png", "wb") as f:
            f.write(graph.get_graph().draw_mermaid_png())
            
        print("Graph visualization rendered and saved to 'graph.png'")
    except Exception as e:
        print(f"Error: Could not render graph: {e}")
        print("Tip: Ensure you have 'pygraphviz' installed or an active internet connection for the Mermaid API.")

if __name__ == "__main__":
    main()
