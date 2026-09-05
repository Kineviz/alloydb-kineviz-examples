WITH pairs AS (SELECT DISTINCT src_client_id AS src,dst_client_id AS dst FROM fraud_demo.paid)
SELECT a.src AS a,a.dst AS b,b.dst AS c,c.dst AS d
FROM pairs a JOIN pairs b ON a.dst=b.src
JOIN pairs c ON b.dst=c.src JOIN pairs d ON c.dst=d.src AND d.dst=a.src
WHERE a.src<a.dst AND a.src<b.dst AND a.src<c.dst
  AND a.dst<>b.dst AND a.dst<>c.dst AND b.dst<>c.dst ORDER BY a,b,c,d;
