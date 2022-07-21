# Eco-Driving Web Application

## Dependencies
Required dependencies that must be installed for the web app to run. Other
dependency versions may be compatible but only those listed have been tested 
and are known to work.

- Node.js v16.14.2
- npm v8.5.5
- PostgreSQL v14

Running `npm install` will install all remaining dependencies.


## Setup
To setup the web app, first run:
```
npm run setup
```

After which, create a config.js file using [config_default.js](config_default.js)
as a template, replacing any values as necessary. You should only need to change
the database user and password values for the web app to run.

If you wish to use your own Auth0 tenant for the web application, setup
instructions can be found in [doc/auth0_setup.md](doc/auth0_setup.md).


## Usage
To run the web application, run:
```
npm start
```

Once running, it will be reachable at [http://localhost:8080](http://localhost:8080).
Ensure third-party cookies are enabled for `http://localhost:8080`, otherwise
Auth0 will be unable to authenticate you.

### Example Data
Example data is provided and can be applied once you have created an account
using the web application. You will be able to apply the example data by running:
```
npm run example-data
```

The example data will be applied to the user with the usr_id of 1, so ensure
your account is the first account created on the web application. 


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
