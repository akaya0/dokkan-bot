# Dokkan EZA Bot
![ddmugb2-b79a8d4f-76ba-4005-8e20-4650b661b134](https://github.com/user-attachments/assets/5f0395c8-05c8-44b0-b617-561ac1bd2d50)

This program connects to an Android device using ADB (Android Debug Bridge), captures screenshots, and processes these images using OpenCV. It includes functionalities for image matching and type/depth consistency checks.

## Requirements

- Python 3.x
- OpenCV
- NumPy
- adbutils
- ADB (Android Debug Bridge)

## Installation

1. Install Python from the [official website](https://www.python.org/).
2. Install ADB on your system. Follow the instructions [here](https://developer.android.com/studio/command-line/adb) to set it up.
3. Clone this repository and navigate to the project directory:
    ```bash
    git clone https://github.com/dokkan-bot.git
    cd dokkan-bot
    ```
4. Install the required Python libraries using pip:
    ```bash
    pip install opencv-python-headless numpy adbutils
    ```

## Usage

1. Ensure your Android device is connected to your computer with USB debugging enabled.
2. Choose the EZA to farm
3. Run the script:
    ```bash
    python main.py
    ```

## Troubleshooting

- **Device not found**: Ensure that your device is connected and USB debugging is enabled. Run `adb devices` to check if your device is listed.
- **Templates not found on Screen**: Even though there are error checks your device might need their own screenshots taken, replace templates accordingly.
- **Virtual Environment** I strongly advice using conda/venv, because i got no clue what im actually doing. 🫡❤️

## To-Do

- **Difficulty Selection** I think it's fine as is to just farm infinitely, but I definitely need to add difficulty selection for coin farming
- **Story Mode**: Self-explanatory
- **Tournament**: I think the most important one is to add a tournament support, I mean at a normal rate there's no way to beat it otherwise?!

## Disclaimer

This software is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and noninfringement. In no event shall the authors be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the software or the use or other dealings in the software. **Use this script at your own risk.**

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [OpenCV](https://opencv.org/)
- [NumPy](https://numpy.org/)
- [adbutils](https://github.com/yt-dlp/yt-dlp)
- [ADB](https://developer.android.com/studio/command-line/adb)
