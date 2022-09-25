<h1 style="text-align: center;">Razer Battery</h1>

A simple system tray to display the Razer mouse battery.

You can specify the mouse and adjust the frequency(minutes) of battery updates using the slider.

<img src="https://raw.githubusercontent.com/Maasea/razerBattery/main/imags/display.png" width="200" height="200">

## For user

The exe or zip file can be downloaded directly from the [release ](https://github.com/Maasea/razerBattery/releases) page.

exe: small but slower startup

zip: faster startup but  bigger

**Note**: 

- All the file requires 64-bit system, but you can build 32-bit files by referring to the `For dev`
- Configuration file directory: `user/username/razerbattery.ini`

## For dev

1. You need download [libusb](https://libusb.info/), and put `libusb-1.0.dll` in the project's root directory.

2. If you want to build 32-bit file, please install 32-bit `python`

3. Install python dependencies

   ```python
   pip install -r requirements.txt
   ```

4. Build

   ```python
   pip install pyinstaller
   ```

   ```python
   # Build to folder
   pyinstaller folder.spec 
   # or build to OneFile
   pyinstaller oneFile.spec
   ```

**Note**: You can get more detailed information by reading  [razer-mouse-battery-windows](https://github.com/hsutungyu/razer-mouse-battery-windows).

## Credit

This project is dependent on  [razer-mouse-battery-windows](https://github.com/hsutungyu/razer-mouse-battery-windows).

