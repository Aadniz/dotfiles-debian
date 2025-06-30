import pyjson5 as json5


def read_config(path: str) -> dict:
    try:
        with open(path, 'r') as f:
            content = f.read()
            config = json5.loads(content)
            return config
    except FileNotFoundError:
        print(f"Error: {path} not found in current directory")
        exit(1)
    except json5.Json5DecoderException as e:
        print(f"Error parsing {path}: {e}")
        exit(1)