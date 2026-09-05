SELECT g.id AS gateway,s.name AS site,count(*) AS devices
FROM fleet_demo.connectedto c JOIN fleet_demo.gateway g ON g.id=c.gateway_id
JOIN fleet_demo.hostedat h ON h.gateway_id=g.id JOIN fleet_demo.site s ON s.id=h.site_id
GROUP BY g.id,s.name ORDER BY devices DESC,gateway;
