import configImport from '../config.js';

const configs: Record<string, any> = configImport;

// Set Config
// --------------------------------------------
let config: {
    auth: {
        domain: string;
        clientID: string;
        audience: string;
        callbackURL: string;
    };
    db: {
        host: string;
        database: string;
        user: string;
        password: string;
    };
};

if (process.env.NODE_ENV) {
    if (configs.hasOwnProperty(process.env.NODE_ENV)) {
        config = configs[process.env.NODE_ENV];
    } else {
        throw Error(`Environment '${process.env.NODE_ENV}' does not exist within config`);
    }
} else {
    if (configs.default) {
        config = configs.default;
    } else {
        throw Error(`Default config does not exist`);
    }
}

export default config;
