export default {
    default: {
        auth: {
            domain: 'jack-d-dev.eu.auth0.com',
            clientID: 'lFNXUOM6yWbfqfvITdXB7dtwCL0oSics',
            audience: 'http://localhost:8080/api',
            scope: 'openid',
            callbackURL: 'http://localhost:8080/auth/callback',
        },
        db: {
            host: process.env.DB_HOST || 'localhost',
            database: 'ecodriven',
            user: 'postgres',
            password: 'postgres',
        },
    },
    testing: {
        auth: {
            domain: 'https://issuer.example.com/',
            audience: 'https://api/',
        },
        db: {
            host: 'localhost',
            database: 'ecodriven_test',
            user: 'postgres',
            password: 'postgres',
        },
    },
};