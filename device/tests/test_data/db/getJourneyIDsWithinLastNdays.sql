-- Current date in tests will be 2022-02-01 
-- ----------------------------------------------
-- On current date
INSERT INTO journey (passenger_cnt, cargo_weight, roof_att_id)
    VALUES (0, 0, null) RETURNING journey_id;
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-02-01 15:00:00', 1, 0, 0, 0, 0, 0, 0, False, 0);

-- At current day limit
INSERT INTO journey (passenger_cnt, cargo_weight, roof_att_id)
    VALUES (0, 0, null) RETURNING journey_id;
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-02-01 00:00:00', 2, 0, 0, 0, 0, 0, 0, False, 0);

-- At current day limit
INSERT INTO journey (passenger_cnt, cargo_weight, roof_att_id)
    VALUES (0, 0, null) RETURNING journey_id;
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-01-31 23:59:59', 3, 0, 0, 0, 0, 0, 0, False, 0);

-- 5 days ago
-- ---------------------
-- On 5th day
INSERT INTO journey (passenger_cnt, cargo_weight, roof_att_id)
    VALUES (0, 0, null);
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-01-27 13:12:00', 4, 0, 0, 0, 0, 0, 0, False, 0);

-- At 5 day limit
INSERT INTO journey (passenger_cnt, cargo_weight, roof_att_id)
    VALUES (0, 0, null);
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-01-27 00:00:00', 5, 0, 0, 0, 0, 0, 0, False, 0);

-- 1 second over 5 day limit 
INSERT INTO journey (passenger_cnt, cargo_weight, roof_att_id)
    VALUES (0, 0, null);
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-01-26 23:59:59', 6, 0, 0, 0, 0, 0, 0, False, 0);

-- 30 days ago
-- ---------------------
-- On 30th day
INSERT INTO journey (passenger_cnt, cargo_weight, roof_att_id)
    VALUES (0, 0, null);
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-01-02 12:35:00', 7, 0, 0, 0, 0, 0, 0, False, 0);

-- At 30 day limit
INSERT INTO journey (passenger_cnt, cargo_weight, roof_att_id)
    VALUES (0, 0, null);
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-01-02 00:00:00', 8, 0, 0, 0, 0, 0, 0, False, 0);

-- 1 second over 30 day limit 
INSERT INTO journey (passenger_cnt, cargo_weight, roof_att_id)
    VALUES (0, 0, null);
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-01-01 23:59:59', 9, 0, 0, 0, 0, 0, 0, False, 0);
