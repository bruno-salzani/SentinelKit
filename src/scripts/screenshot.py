import os
import time
from datetime import datetime
import support

def main():
    support.ensure_dependencies(["mss"])
    import mss
    import mss.tools
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(root, "results", "screenshots")
    os.makedirs(out_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(out_dir, "screenshot_{0}.png".format(ts))
    with mss.mss() as sct:
        mon = sct.monitors[1]
        img = sct.grab(mon)
        mss.tools.to_png(img.rgb, img.size, output=path)
    print(path)

if __name__ == "__main__":
    main()
