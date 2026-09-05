CREATE VIEW covers_v AS SELECT jsonb_build_array(technician_id,site_id)::text AS eid,* FROM covers;
CREATE VIEW dependson_v AS SELECT jsonb_build_array(device_id,depends_on_id)::text AS eid,* FROM dependson;
CREATE PROPERTY GRAPH fleet_graph
VERTEX TABLES (
 site KEY(id) LABEL site PROPERTIES ALL COLUMNS,
 gateway KEY(id) LABEL gateway PROPERTIES ALL COLUMNS,
 device KEY(id) LABEL device PROPERTIES ALL COLUMNS,
 firmware KEY(id) LABEL firmware PROPERTIES ALL COLUMNS,
 technician KEY(id) LABEL technician PROPERTIES ALL COLUMNS
)
EDGE TABLES (
 hostedat KEY(gateway_id) SOURCE KEY(gateway_id) REFERENCES gateway(id) DESTINATION KEY(site_id) REFERENCES site(id) LABEL hosted_at PROPERTIES(gateway_id,rack),
 connectedto KEY(device_id) SOURCE KEY(device_id) REFERENCES device(id) DESTINATION KEY(gateway_id) REFERENCES gateway(id) LABEL connected_to PROPERTIES(device_id,port),
 runsfirmware KEY(device_id) SOURCE KEY(device_id) REFERENCES device(id) DESTINATION KEY(firmware_id) REFERENCES firmware(id) LABEL runs PROPERTIES(device_id,applied_date),
 covers_v KEY(eid) SOURCE KEY(technician_id) REFERENCES technician(id) DESTINATION KEY(site_id) REFERENCES site(id) LABEL covers PROPERTIES(eid,since_date),
 dependson_v KEY(eid) SOURCE KEY(device_id) REFERENCES device(id) DESTINATION KEY(depends_on_id) REFERENCES device(id) LABEL depends_on PROPERTIES(eid,reason)
);
