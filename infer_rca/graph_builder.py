import os
import ast

def analyze_directory(directory_path):
    """
    Scans a directory, reads Python files using AST, 
    and outputs React Flow nodes and edges.
    """
    nodes = []
    edges = []
    
    file_list = [f for f in os.listdir(directory_path) if f.endswith('.py')]
    
    for index, filename in enumerate(file_list):
        nodes.append({
            "id": filename,
            "position": {"x": 250, "y": index * 100 + 50},
            "data": {"label": filename}
        })

    for filename in file_list:
        filepath = os.path.join(directory_path, filename)
        
        with open(filepath, "r", encoding="utf-8") as file:
            try:
                tree = ast.parse(file.read(), filename=filename)
            except SyntaxError:
                continue 
                
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    target_file = f"{alias.name}.py"
                    if target_file in file_list:
                        edges.append({
                            "id": f"e-{filename}-{target_file}",
                            "source": filename,
                            "target": target_file,
                            "animated": True
                        })
                        
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    target_file = f"{node.module}.py"
                    if target_file in file_list:
                        edges.append({
                            "id": f"e-{filename}-{target_file}",
                            "source": filename,
                            "target": target_file,
                            "animated": True
                        })
                        
    return {"nodes": nodes, "edges": edges}

if __name__ == "__main__":
    import json
    graph_data = analyze_directory("../sandbox")
    print(json.dumps(graph_data, indent=2))