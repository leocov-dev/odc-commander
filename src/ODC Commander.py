import argparse
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ODC Commander")
    parser.add_argument("--debug", action="store_true", help="Debug mode, shows additional logging")

    args = parser.parse_args()

    os.environ["LOGURU_LEVEL"] = "DEBUG" if args.debug else "WARNING"

    from odc_commander.app import OdcCommanderApp

    OdcCommanderApp().launch()
