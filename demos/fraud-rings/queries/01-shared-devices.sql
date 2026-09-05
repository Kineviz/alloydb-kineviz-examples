SELECT device_id, count(DISTINCT client_id) AS accounts
FROM fraud_demo.useddevice GROUP BY device_id
HAVING count(DISTINCT client_id)>1 ORDER BY accounts DESC,device_id;
