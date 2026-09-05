-- Canonicalize by minimum account ID; distinct payment pairs avoid multiplying
-- cycles when the same pair has several payments. Bound the walk to four hops.
WITH pairs AS (
  SELECT DISTINCT sender_id, receiver_id FROM paysim_demo.payments
  WHERE receiver_type='client' AND action='TRANSFER'
)
SELECT DISTINCT a.sender_id AS a, a.receiver_id AS b, b.receiver_id AS c, c.receiver_id AS d
FROM pairs a JOIN pairs b ON b.sender_id=a.receiver_id
JOIN pairs c ON c.sender_id=b.receiver_id
JOIN pairs d ON d.sender_id=c.receiver_id AND d.receiver_id=a.sender_id
WHERE a.sender_id<a.receiver_id AND a.sender_id<b.receiver_id AND a.sender_id<c.receiver_id
  AND a.receiver_id<>b.receiver_id AND a.receiver_id<>c.receiver_id
  AND b.receiver_id<>c.receiver_id ORDER BY a,b,c,d;
