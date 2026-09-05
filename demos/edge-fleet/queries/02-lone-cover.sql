SELECT s.id,s.name,min(t.name) AS technician
FROM fleet_demo.site s JOIN fleet_demo.covers c ON c.site_id=s.id
JOIN fleet_demo.technician t ON t.id=c.technician_id
GROUP BY s.id,s.name HAVING count(DISTINCT t.id)=1 ORDER BY s.id;
