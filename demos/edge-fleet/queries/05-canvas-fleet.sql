SELECT d.id AS device_id,d.kind,d.criticality,g.id AS gateway_id,g.model,
       s.id AS site_id,s.name AS site_name,s.region
FROM fleet_demo.device d JOIN fleet_demo.connectedto c ON c.device_id=d.id
JOIN fleet_demo.gateway g ON g.id=c.gateway_id
JOIN fleet_demo.hostedat h ON h.gateway_id=g.id JOIN fleet_demo.site s ON s.id=h.site_id
ORDER BY d.id LIMIT 500;
