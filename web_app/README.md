# Eco-Driving Web Application

## Docker
The web app can be run with Docker using:
```
docker compose up -d
```

Once running, head to [http://localhost:8080](http://localhost:8080). Ensure
third-party cookies are enabled, otherwise Auth0 will be unable to authenticate
you.

The app will run in demo mode, which will apply some example data to the first
account created, allowing you to see how the web app functions without needing a
running eco-driving device.

By default, the docker configuration will automatically copy [config_default.js](config_default.js)
to use as the config. You are free to create and configure your own `config.js`
file from [config_default.js](config_default.js) and it will be used instead.
However, you may need to rebuild your image  by applying the `--build` flag if
you have already run `docker compose up -d`.


## Manual Installation
### Dependencies
Required dependencies that must be installed for the web app to run. Other
dependency versions may be compatible but only those listed have been tested 
and are known to work.

- Node.js v16.14.2
- npm v8.5.5
- PostgreSQL v14

Running `npm install` will install all remaining dependencies.

### Setup
To setup the web app, first run:
```
npm run setup
```

After which, create a `config.js` file using [config_default.js](config_default.js)
as a template, replacing any values if needed.

### Usage
The web app can be run with:
```
npm start
```

Once running, it will be reachable at [http://localhost:8080](http://localhost:8080).
Ensure third-party cookies are enabled for `http://localhost:8080`, otherwise
Auth0 will be unable to authenticate you.

### Demo Mode
Example data is provided and can be used by running the web app in demo mode.
Demo mode will apply the example data to the first account created, allowing you
to see how the web app functions without needing a running eco-driving device.

To use demo mode, run:
```
npm run demo
```


## Setting Up Your Own Auth0 Tenant
If you wish to use your own Auth0 tenant for the web application, setup
instructions can be found in [doc/auth0_setup.md](doc/auth0_setup.md).


## Testing
To run tests, run:
```
npm test
```

### Coverage
Test coverage information is reported at the end of testing. Additionally, the
Web App CI action generates a coverage report that can be found in
[doc/coverage/](doc/coverage/).


## npm Scripts
To view all of the available npm scripts with descriptions, read
[doc/npm_scripts.md](doc/npm_scripts.md).


## API Reference
API reference documentation can be found at
[http://localhost:8080/api-docs](http://localhost:8080/api-docs) when the web
application is running.


## Code Documentation
Code documentation can be found in [doc/client/](doc/client/) for code in
[public/](public) and [doc/server/](doc/server/) for code in [src/](src).
