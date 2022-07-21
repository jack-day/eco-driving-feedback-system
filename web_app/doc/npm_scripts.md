# npm Scripts

## start
Compiles the typescript code in [src](../src) to the `dist` directory and runs
the web app.
```
npm start
```

## dev
Runs a development environment for the web app that executes the typescript code
without precompiling and restarts when changes are made.
```
npm run dev
```

## test
Runs the web app's unit tests using Jest.
```
npm test
```

## setup
Create and intialises the web app's regular and testing database.
```
npm run setup
```

### setup:app
Only creates and intialises the web app's regular database.
```
npm run setup:app
```

### setup:tests
Only creates and intialises the web app's testing database.
```
npm run setup:tests
```

## example-data
Applies example-data to the user's account after it has been created. The
example data will be applied to the user with the usr_id of 1, so ensure
your account is the first account created on the web application. 
```
npm run example-data
```

## docs
Generates the code documentation for the client and the server.
```
npm run docs
```

### docs:server
Only generates the code documentation for the server.
```
npm run docs:server
```

### docs:client
Only generates the code documentation for the client.
```
npm run docs:client
```

## lint
Runs ESLint and Stylelint to check for linting errors.
```
npm run lint
```

### lint:eslint
Only runs eslint.
```
npm run lint:eslint
```

### lint:stylelint
Only runs stylelint.
```
npm run lint:stylelint
```
