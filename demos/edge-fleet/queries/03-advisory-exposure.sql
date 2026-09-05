SELECT f.advisory,count(*) AS devices
FROM fleet_demo.runsfirmware r JOIN fleet_demo.firmware f ON f.id=r.firmware_id
WHERE f.advisory IS NOT NULL AND f.advisory<>'' GROUP BY f.advisory ORDER BY devices DESC;
