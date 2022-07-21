# Assetto Corsa Apps 
These files contain Assetto Corsa apps developed for this project.

To install an app:
- Place the app's folder in the Assetto Corsa files under `\assettocorsa\apps\python`.
- Enable the app in Assetto Corsa, under Options > General > UI Modules. For
  example, enabling the OBD2 app would look like:

  ![Assetto Corsa OBD2 App Location](/doc/img/assetto_corsa_obd2.png)


## OBD2
Retrieves and sends the requested simulated ECU data to the [OBD emulator](/device/device/obd_ii.py)
utilising Assetto Corsa's python module and shared memory.

The `/lib` and `sim_info.py` files have been obtained from the official Assetto
Corsa modding forums [here](https://www.assettocorsa.net/forum/index.php?threads/shared-memory-for-python-applications-sim_info-py-for-ac-v0-22.11382/).

### Resources
[Getting started with Assetto Corsa application development](https://assettocorsamods.net/threads/getting-started-with-ac-app-developing.716/)

[Assetto Corsa Python Documentation](https://docs.google.com/document/d/13trBp6K1TjWbToUQs_nfFsB291-zVJzRZCNaTYt4Dzc/pub)

[Assetto Corsa Shared Memory Reference](https://assettocorsamods.net/threads/doc-shared-memory-reference.58/)

## Tachometer
A simple tachometer, displaying the current RPM numerically, created to assist
in testing.

![Tachometer Screenshot](/doc/img/assetto_corsa_tachometer.png)
