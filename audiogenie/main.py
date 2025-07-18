import sys
from config_loader import ConfigLoader
from pipeline import AudioPipeline

def main(config_path):
    config_loader = ConfigLoader(config_path)
    config = config_loader.load()

    pipeline = AudioPipeline(config)
    results = pipeline.run()

    print("Pipeline finished.")
    print("Outputs:")
    for key, files in results.items():
        print(f"{key}:")
        for f in files:
            print(f"  - {f}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <path_to_config.json>")
        sys.exit(1)

    main(sys.argv[1])
