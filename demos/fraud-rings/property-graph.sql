CREATE VIEW useddevice_v AS SELECT jsonb_build_array(client_id,device_id)::text AS eid,* FROM useddevice;
CREATE PROPERTY GRAPH fraud_graph
VERTEX TABLES (
 client KEY(id) LABEL client PROPERTIES ALL COLUMNS,
 device KEY(id) LABEL device PROPERTIES ALL COLUMNS,
 merchant KEY(id) LABEL merchant PROPERTIES ALL COLUMNS
)
EDGE TABLES (
 useddevice_v KEY(eid) SOURCE KEY(client_id) REFERENCES client(id) DESTINATION KEY(device_id) REFERENCES device(id) LABEL used_device PROPERTIES(eid,first_used),
 paid KEY(tx_id) SOURCE KEY(src_client_id) REFERENCES client(id) DESTINATION KEY(dst_client_id) REFERENCES client(id) LABEL paid PROPERTIES(tx_id,amount,ts),
 paidmerchant KEY(tx_id) SOURCE KEY(client_id) REFERENCES client(id) DESTINATION KEY(merchant_id) REFERENCES merchant(id) LABEL paid_merchant PROPERTIES(tx_id,amount,ts)
);
