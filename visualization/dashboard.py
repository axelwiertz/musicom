"""Dashboard stub."""

def generate_dashboard(matrix, path):
    """Stub dashboard generator."""
    import os
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write("""<!doctype html>
<html><head><title>Music Dashboard</title></head><body>
<h1>Music Dashboard</h1><p>Matrix rendered.</p></body></html>""")
    return True