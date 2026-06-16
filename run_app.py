import os
import sys
import streamlit.web.cli as stcli

def resolve_path(path):
    """
    Resolves the absolute path to a resource.
    When packaged by PyInstaller, files are extracted to a temporary folder 
    defined by sys._MEIPASS. Otherwise, it uses the current directory.
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, path)
    return os.path.join(os.path.abspath('.'), path)

if __name__ == "__main__":
    # We must explicitly set the path to app.py so Streamlit can find it 
    # when unpacked from the exe.
    app_path = resolve_path("app.py")
    sys.argv = ["streamlit", "run", app_path, "--global.developmentMode=false"]
    sys.exit(stcli.main())
