# Providing Continuous Eco-Driving Feedback Across Multiple Feedback Methods

> University Final Year Engineering Project

## Abstract
Global warming is an alarming threat for the planet’s future and efforts
must be made to reduce emissions. The transport sector is one of the largest
contributors to global emissions, with research showing that light-duty vehicles contribute to approximately 40% of total transport emissions. Driver
behaviour is a primary factor of light-duty vehicle emissions and can be improved through eco-driving. Eco-driving is a driving style that increases
vehicle fuel efficiency and consequently reduces vehicle emissions. However,
developing new eco-driving habits can be difficult without consistent feedback or guidance. Eco-driving devices are a platform to provide this, but they
often only produce short-term effects and do not utilise multiple effective
feedback methods. This project aims to research and develop an eco-driving
device that assists in improving driver behaviour and emissions over the long-term by providing continuous feedback on a driver’s eco-driving habits using
multiple feedback methods. Based on a review of the literature on vehicle
emissions, eco-driving, and eco-driving devices, requirements were gathered
to meet the project’s objective. An eco-driving feedback system consisting
of an eco-driving device and an accompanying web application were subsequently designed and developed to satisfy the gathered requirements. The
implemented eco-driving feedback system successfully provides effective eco-driving feedback and satisfies the project’s must have requirements. Overall, the produced eco-driving feedback system provides a proof of concept,
demonstrating how multiple feedback methods can be used to improve driver
behaviour over the long term and reduce vehicle emissions.

## Demo Video
A video demonstrating the project's main functionalities can be found at: [https://youtu.be/LVWXPqs2o1M](https://youtu.be/LVWXPqs2o1M).


## Eco-driving Device Software
The software for the eco-driving device can be found in [device/](device/).


## Eco-Driving Web Application
The web application for the eco-driving device can be found in [web_app/](web_app/).


## Assetto Corsa App
The Assetto Corsa App used to retrieve and send the simulated ECU Data to the
OBD emulator can be found in [assettocorsa/](assettocorsa/).


## Documentation
Documentation for the project can be found in [doc/](doc/). The device and web
app also include their own documentation in a sub-directory of the same name
within their respective directories.


## File Structure
```
/
|-- .github/
    |-- workflows/                      - GitHub actions for continuous integration
|-- assettocorsa/                       - Assetto Corsa app code
    |-- OBD2/                           - OBD-II app to collect simulated ECU data
|-- device/                             - Eco-driving device code
    |-- adafruit/                       - Device display setup files
    |-- assets/                         - Display assets
    |-- db/                             - Database setup
    |-- device/                         - Device Source code
        |-- init.py
        |-- main.py                     - Device entry point
    |-- doc/                            - Developer documentation
        |-- html/                       - Code documentation
        |-- coverage.md                 - Unit test coverage
    |-- tests/                          - Unit tests
    |-- config.ini                      - Device configuration
    |-- gps.yaml                        - GPS coordinates for simulation
    |-- requirements.txt                - PyPI dependencies
    |-- requirements_dev.txt            - PyPI dependencies for development
    |-- settings.yaml                   - Settings, such as vehicle specifications
|-- web_app/                            - Web application code
    |-- db/                             - Database setup
    |-- doc/                            - Developer documentation
        |-- client/                     - Client-side code documentation
        |-- coverage/                   - Unit test coverage
        |-- server/                     - Server code documentation
    |-- public/                         - Client-side static content
        |-- assets/
            |-- icon/                   - Icon files
            |-- img/                    - Image files
        |-- css/                        - CSS styling
        |-- js/                         - Client-side JavaScript
            |-- modules/                - Functionality used by multiple pages
    |-- src/                            - Server source code
        |-- @types/                     - Additional npm package type definitions
        |-- {component}                 - API resource as a self-contained component
            |-- controllers.ts          - Route handling logic
            |-- data_access.ts          - Data access layer for database interaction
            |-- routes.ts               - Express API routes
            |-- services                - Business logic
        |-- api.ts                      - REST API routes
        |-- app.ts                      - App entry point
    |-- swagger/                        - Swagger API documentation files
    |-- tests/                          - Server unit tests
    |-- config.js                       - Web app configuration
    |-- package.json                    - Node.js project metadata, such as dependencies
```
