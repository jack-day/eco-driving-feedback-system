-- FUNCTIONS
-------------------------------------------------
-- Checks value is between low and high as BETWEEN does not work in check constraints
CREATE FUNCTION btwn(val REAL, low INTEGER, high INTEGER, allow_null BOOLEAN DEFAULT TRUE)
    RETURNS boolean
    LANGUAGE plpgsql AS
$$
BEGIN
    RETURN (CASE WHEN val IS NOT NULL THEN
        low <= val AND val <= high
    ELSE
        allow_null
    END);
END
$$;

-- TABLES
-------------------------------------------------
CREATE TABLE usr (
    usr_id SERIAL PRIMARY KEY,
    auth0_user_id TEXT NOT NULL UNIQUE
);

CREATE TABLE journey (
    usr_id INTEGER REFERENCES usr(usr_id) ON DELETE CASCADE,
    journey_id SERIAL,
    PRIMARY KEY (usr_id, journey_id),
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL CONSTRAINT end_time_after_start_time CHECK(end_time > start_time),
    idle_secs INTEGER NOT NULL CONSTRAINT idle_secs_is_positive CHECK(idle_secs >= 0),
    distance REAL NOT NULL CONSTRAINT distance_is_positive CHECK(distance >= 0),
    gsi_adh REAL CONSTRAINT gsi_adh_is_pct CHECK(btwn(gsi_adh, 0, 100))
);

CREATE TABLE scores (
    usr_id INTEGER REFERENCES usr(usr_id) ON DELETE CASCADE,
    calculated_at TIMESTAMPTZ,
    PRIMARY KEY (usr_id, calculated_at),
    eco_driving INTEGER NOT NULL CONSTRAINT eco_driving_is_score CHECK(btwn(eco_driving, 0, 100, FALSE)),
    driv_acc_smoothness INTEGER CONSTRAINT driv_acc_smoothness_is_score CHECK(btwn(driv_acc_smoothness, 0, 100)),
    start_acc_smoothness INTEGER CONSTRAINT start_acc_smoothness_is_score CHECK(btwn(start_acc_smoothness, 0, 100)),
    dec_smoothness INTEGER CONSTRAINT dec_smoothness_is_score CHECK(btwn(dec_smoothness, 0, 100)),
    gsi_adh INTEGER CONSTRAINT gsi_adh_is_score CHECK(btwn(gsi_adh, 0, 100)),
    speed_limit_adh INTEGER CONSTRAINT speed_limit_adh_is_score CHECK(btwn(speed_limit_adh, 0, 100)),
    motorway_speed INTEGER CONSTRAINT motorway_speed_is_score CHECK(btwn(motorway_speed, 0, 100)),
    idle_duration INTEGER CONSTRAINT idle_duration_is_score CHECK(btwn(idle_duration, 0, 100)),
    journey_idle_pct INTEGER CONSTRAINT journey_idle_pct_is_score CHECK(btwn(journey_idle_pct, 0, 100)),
    journey_distance INTEGER CONSTRAINT journey_distance_is_score CHECK(btwn(journey_distance, 0, 100))
);
