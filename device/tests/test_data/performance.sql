-- Journey without Driving Data
-- ----------------------------------------------
INSERT INTO journey (passenger_cnt, cargo_weight, roof_att_id)
    VALUES (0, 0, null) RETURNING journey_id;


-- Journey with 1 Driving Data entry
-- ----------------------------------------------
INSERT INTO journey (passenger_cnt, cargo_weight, roof_att_id)
    VALUES (0, 0, null) RETURNING journey_id;
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-02-03 00:00:00', 2, 10, 11, 12, 13, 14, 15, False, null);

-- Journey with 2 Driving Data entries
-- ----------------------------------------------
INSERT INTO journey (passenger_cnt, cargo_weight, roof_att_id)
    VALUES (0, 0, null) RETURNING journey_id;
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-02-02 00:00:00', 3, 10, 11, 12, 13, 14, 15, False, null);
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-02-02 00:00:01', 3, 10, 11, 12, 13, 14, 15, True, 9);

-- Journey with full mock data
-- ----------------------------------------------
INSERT INTO journey (passenger_cnt, cargo_weight, roof_att_id)
    VALUES (0, 0, null) RETURNING journey_id;
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-02-01 00:00:00', 4, 0, 0, 100, 1, 2, 3, False, 48);
-- Acceleration: 1.388889 m/s2, Distance: 0.6944445 m
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-02-01 00:00:01', 4, 5, 1500, 99.8, 1, 2, 3, False, 48);
-- Acceleration: 1.388889 m/s2, Distance: 2.0833335 m
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-02-01 00:00:02', 4, 10, 1750, 99.6, 1, 2, 3, False, 48);
-- Acceleration: 2.777778 m/s2, Distance: 4.166667 m
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-02-01 00:00:03', 4, 20, 2200, 99.4, 1, 2, 3, True, 48);
-- Acceleration: 5.555556 m/s2, Distance: 8.333334 m
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-02-01 00:00:04', 4, 40, 2000, 99.2, 1, 2, 3, True, 48);
-- Acceleration: 5.555556 m/s2, Distance: 13.88889 m
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-02-01 00:00:05', 4, 60, 1800, 99, 1, 2, 3, False, 48);
-- Acceleration: 5.555556 m/s2, Distance: 19.444446 m
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-02-01 00:00:06', 4, 80, 2200, 98.8, 1, 2, 3, True, null);
-- Acceleration: 8.333334 m/s2, Distance: 26.388891 m
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-02-01 00:00:07', 4, 110, 1600, 98, 1, 2, 3, False, 113);
-- Acceleration: 2.777778 m/s2, Distance: 31.944447 m
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-02-01 00:00:08', 4, 120, 1700, 97.8, 1, 2, 3, False, 113);
-- Acceleration: -1.9444446 m/s2, 32.3611137 m
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-02-01 00:00:09', 4, 113, 1650, 97.6, 1, 2, 3, False, 113);
-- Acceleration: 0 m/s2, 125.5555656 m
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-02-01 00:00:13', 4, 113, 1650, 97.6, 1, 2, 3, False, 113);
-- Acceleration: -14.5833345 m/s2, 24.09722415 m
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-02-01 00:00:14', 4, 60.5, 1300, 97.4, 1, 2, 3, False, 113);
-- Acceleration: -4.3055559 m/s2, 14.65277895 m
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-02-01 00:00:15', 4, 45, 1600, 97, 1, 2, 3, False, 48);
-- Acceleration: -12.500001 m/s2, 6.2500005 m
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-02-01 00:00:16', 4, 0, 1600, 96.8, 1, 2, 3, False, 48);
-- Acceleration: 0 m/s2, 0 m
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-02-01 00:00:21', 4, 0, 1600, 96.6, 1, 2, 3, False, 48);
-- Acceleration: 2.777778 m/s2, 1.388889 m
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-02-01 00:00:22', 4, 10, 1600, 96.4, 1, 2, 3, False, 48);
-- Acceleration: -2.777778 m/s2, 1.388889 m
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-02-01 00:00:23', 4, 0, 1600, 96.4, 1, 2, 3, False, 48);
-- Acceleration: 0 m/s2, 0 m
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-02-01 00:00:32', 4, 0, 1600, 95.6, 1, 2, 3, False, 48);
-- Acceleration: 0 m/s2, 0 m
INSERT INTO driving_data (time, journey_id, engine_on, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-02-01 00:00:38', 4, FALSE, 0, 1600, 95.6, 1, 2, 3, False, 48);
-- Acceleration: 0 m/s2, 0 m
INSERT INTO driving_data (time, journey_id, engine_on, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-02-01 00:00:50', 4, True, 0, 1600, 95.6, 1, 2, 3, False, 48);
-- Acceleration: 0 m/s2, 0 m
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-02-01 00:00:57', 4, 0, 1600, 95.6, 1, 2, 3, False, 48);

-- 2nd journey with mock data
-- ----------------------------------------------
INSERT INTO journey (passenger_cnt, cargo_weight, roof_att_id)
    VALUES (0, 0, null) RETURNING journey_id;
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-01-02 00:00:00', 5, 0, 0, 100, 1, 2, 3, False, 48);
-- Acceleration: 4.166667 m/s2, Distance: 2.0833335 m
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-01-02 00:00:01', 5, 15, 2100, 99.8, 1, 2, 3, True, 48);
-- Acceleration: 9.722223 m/s2, Distance: 9.0277785 m
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-01-02 00:00:02', 5, 50, 2200, 99.6, 1, 2, 3, True, 48);
-- Acceleration: 2.0833335 m/s2, Distance: 72.222228 m
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-01-02 00:00:06', 5, 80, 1600, 98.8, 1, 2, 3, False, null);
-- Acceleration: 8.333334 m/s2, Distance: 26.388891 m
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-01-02 00:00:07', 5, 110, 1600, 98, 1, 2, 3, False, 113);
-- Acceleration: 0 m/s2, Distance: 244.444464 m
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-01-02 00:00:15', 5, 110, 1700, 97.8, 1, 2, 3, False, 113);
-- Acceleration: -1.5277779 m/s2,  305.55558 m
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-01-02 00:00:35', 5, 0, 1600, 94, 1, 2, 3, False, 48);
-- Acceleration: 0 m/s2, 0 m
INSERT INTO driving_data (time, journey_id, speed, rpm, fuel_level, altitude, latitude, longitude, gsi_is_indicating, speed_limit)
    VALUES ('2022-01-02 00:02:00', 5, 0, 1600, 95.6, 1, 2, 3, False, 48);

-- Journey with api_journey_id
-- ----------------------------------------------
-- JourneyID: 6
INSERT INTO journey (api_journey_id, passenger_cnt, cargo_weight, roof_att_id)
    VALUES (21, 0, 0, null);

-- Journey without api_journey_id
-- ----------------------------------------------
-- JourneyID: 7
INSERT INTO journey (passenger_cnt, cargo_weight, roof_att_id)
    VALUES (0, 0, null);