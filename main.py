import sys
import webbrowser
import yaml
from pathlib import Path

def main():
    config_path = Path("config.yaml")
    if not config_path.exists():
        print("ERROR: config.yaml not found")
        sys.exit(1)

    with open(config_path) as f:
        config = yaml.safe_load(f)

    host = config.get("host", "127.0.0.1")
    port = config.get("port", 8000)

    print(f"\n🚀 Promo Machine starting at http://{host}:{port}\n")

    import threading
    threading.Timer(2, lambda: webbrowser.open(f"http://{host}:{port}")).start()

    import uvicorn
    uvicorn.run("backend.app:app", host=host, port=port, reload=True)

if __name__ == "__main__":
    main()
