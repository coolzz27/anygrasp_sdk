import sys
import json
import numpy as np
from arm_move import arm_move


def main():
    input_data = json.loads(sys.argv[1])

    translation = np.array(input_data["translation"])
    rotation = np.array(input_data["rotation"])

    try:
        arm_move(translation, rotation)
    except Exception as e:
        print(f"{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
