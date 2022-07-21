import config from './config';
import pg from 'pg';
const { Pool, types } = pg;

/** PostgreSQL Connection */
const pool = new Pool({
    host: config.db.host,
    database: config.db.database,
    user: config.db.user,
    password: config.db.password,
    statement_timeout: 5000,
});

// Set queries to return numbers instead of strings for INT and FLOAT data types
types.setTypeParser(types.builtins.INT2, (value: any) => parseInt(value, 10));
types.setTypeParser(types.builtins.INT4, (value: any) => parseInt(value, 10));
types.setTypeParser(types.builtins.INT8, (value: any) => parseInt(value, 10));
types.setTypeParser(types.builtins.FLOAT4, (value: any) => parseFloat(value));
types.setTypeParser(types.builtins.FLOAT8, (value: any) => parseFloat(value));

export default pool;
