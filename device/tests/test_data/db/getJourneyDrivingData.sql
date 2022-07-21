-- No Driving Data
-- ----------------------------------------------
INSERT INTO journey (passenger_cnt, cargo_weight, roof_att_id)
    VALUES (0, 0, null) RETURNING journey_id;


-- 1 driving data entry
-- ----------------------------------------------
INSERT INTO journey (passenger_cnt, cargo_weight, roof_att_id)
    VALUES (0, 0, null) RETURNING journey_id;
INSERT INTO driving_data (time, journey_id, engine_on, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-02-01 00:00:00', 2, TRUE, 10, 11, 12, 13, 14, 15, True, 16);


-- 5 driving data entries
-- ----------------------------------------------
INSERT INTO journey (passenger_cnt, cargo_weight, roof_att_id)
    VALUES (0, 0, null) RETURNING journey_id;
INSERT INTO driving_data (time, journey_id, engine_on, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-02-02 00:00:00', 3, FALSE, 10, 11, 12, 13, 14, 15, True, 16);
INSERT INTO driving_data (time, journey_id, engine_on, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-02-02 05:00:00', 3, TRUE, 10, 11, 12, 13, 14, 15, True, 16);
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-02-02 10:00:00', 3, 10, 11, 12, 13, 14, 15, True, 16);
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-02-02 15:00:00', 3, 10, 11, 12, 13, 14, 15, True, 16);
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-02-02 20:00:00', 3, 10, 11, 12, 13, 14, 15, True, 16);
