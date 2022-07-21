CREATE EXTENSION IF NOT EXISTS timescaledb;

-- TABLES
-------------------------------------------------
CREATE TABLE roof_att (
    roof_att_id SERIAL PRIMARY KEY,
    name VARCHAR(64) NOT NULL UNIQUE,
    weight INTEGER NOT NULL,    -- kg
    drag_coeff REAL NOT NULL,
    frontal_area REAL NOT NULL  -- metres squared
);

CREATE TABLE journey (
    journey_id SERIAL PRIMARY KEY,
    api_journey_id INTEGER UNIQUE,
    passenger_cnt INTEGER NOT NULL DEFAULT 0,
    cargo_weight INTEGER NOT NULL DEFAULT 0,  -- kg
    roof_att_id INTEGER REFERENCES roof_att(roof_att_id) DEFAULT NULL
);

CREATE TABLE driving_data (
    time TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    journey_id INTEGER NOT NULL REFERENCES journey(journey_id),
    engine_on BOOLEAN NOT NULL DEFAULT TRUE,
    speed REAL NOT NULL,        -- kmh
    rpm INTEGER NOT NULL,
    fuel_level REAL NOT NULL,   -- percentage
    altitude REAL NOT NULL,      -- metres
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    gsi_is_indicating BOOLEAN,
    speed_limit INTEGER        -- kmh
);

SELECT create_hypertable('driving_data','time');
SELECT add_retention_policy('driving_data', INTERVAL '31 days');


-- VIEWS
-------------------------------------------------
CREATE VIEW journey_start_times AS
    SELECT
        dd.journey_id,
        (
            SELECT time FROM driving_data
            WHERE journey_id=dd.journey_id
            ORDER BY time ASC LIMIT 1
        ) AS start_time
    FROM driving_data dd
    GROUP BY dd.journey_id
    ORDER BY journey_id;
