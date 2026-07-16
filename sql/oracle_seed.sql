-- Seed CONCOR-style terminals (run after oracle_schema.sql)
-- Example:
--   sqlplus user/password@//host:1521/SERVICE @sql/oracle_seed.sql
-- Re-run clears and reloads demo rows.

DELETE FROM port_containers;

INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Tughlakabad, New Delhi', 14230);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Dadri, Greater Noida', 13680);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Ballabhgarh, Haryana', 11875);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Rai Sonepat, Haryana', 10250);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Panipat, Haryana', 9640);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Dhandari Kalan, Ludhiana', 9480);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Moradabad, Uttar Pradesh', 8950);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Agra, Uttar Pradesh', 8410);
INSERT INTO port_containers (port_terminal, containers) VALUES ('Multi Modal Logistics Park Kanpur', 8320);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Malanpur, Madhya Pradesh', 8155);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Sabarmati, Ahmedabad', 12540);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Khodiyar, Ahmedabad', 10820);
INSERT INTO port_containers (port_terminal, containers) VALUES ('CFS Dronagiri, Navi Mumbai', 11560);
INSERT INTO port_containers (port_terminal, containers) VALUES ('CONCOR Port Terminal, Jawaharlal Nehru Port', 12200);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Mulund, Mumbai', 9340);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Vadodara, Gujarat', 7920);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Ankleshwar, Gujarat', 7640);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Gandhidham, Gujarat', 8855);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Morbi, Gujarat', 7120);
INSERT INTO port_containers (port_terminal, containers) VALUES ('MMLP Balli, Goa', 5480);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Bhusawal, Maharashtra', 6210);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Nagpur Container Terminal', 8740);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Pune, Maharashtra', 7560);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Aurangabad, Maharashtra', 5890);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Whitefield, Bengaluru', 11240);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Irugur, Coimbatore', 8360);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Sanathnagar, Hyderabad', 9780);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Thimmapur, Hyderabad', 8120);
INSERT INTO port_containers (port_terminal, containers) VALUES ('CFS Tuticorin, Tamil Nadu', 9240);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Chennai Port Side Terminal', 10580);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Tondiarpet, Chennai', 8670);
INSERT INTO port_containers (port_terminal, containers) VALUES ('CFS Cochin, Kerala', 7340);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Mangalore, Karnataka', 6890);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Hosur, Tamil Nadu', 6520);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Krishnapatnam, Andhra Pradesh', 7980);
INSERT INTO port_containers (port_terminal, containers) VALUES ('CFS Visakhapatnam, Andhra Pradesh', 8450);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Kakinada, Andhra Pradesh', 6120);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Madurai, Tamil Nadu', 5740);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Kolkata Dock Terminal', 9120);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Shalimar, Howrah', 7840);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Amingaon, Guwahati', 4980);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Jamshedpur, Jharkhand', 6650);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Raxaul, Bihar', 5320);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Patna, Bihar', 6010);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Raipur, Chhattisgarh', 7280);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Naya Raipur, Chhattisgarh', 5940);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Bhubaneswar, Odisha', 6410);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Paradip Port Terminal', 7020);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Haldia, West Bengal', 7580);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Jaipur, Rajasthan', 8210);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Jodhpur, Rajasthan', 6930);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Kota, Rajasthan', 5640);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Bhiwadi, Rajasthan', 6125);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Udaipur, Rajasthan', 5210);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Baddi, Himachal Pradesh', 4870);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Mandideep, Madhya Pradesh', 6380);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Indore Pithampur, Madhya Pradesh', 7710);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Rewari, Haryana', 8540);
INSERT INTO port_containers (port_terminal, containers) VALUES ('ICD Faridabad, Haryana', 8020);
INSERT INTO port_containers (port_terminal, containers) VALUES ('CFS Amritsar, Punjab', 5560);

COMMIT;

SELECT COUNT(*) AS row_count FROM port_containers;
SELECT port_terminal, containers FROM port_containers ORDER BY containers DESC FETCH FIRST 5 ROWS ONLY;
