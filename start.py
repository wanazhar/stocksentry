
import streamlit.web.cli as stcli
import sys

if __name__ == "__main__":
    sys.argv = ["streamlit", "run", "main.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true", "--browser.serverAddress=0.0.0.0"]
    sys.exit(stcli.main())
