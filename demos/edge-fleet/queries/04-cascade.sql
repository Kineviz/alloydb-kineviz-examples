WITH RECURSIVE walk(root,dependent,path,depth) AS (
  SELECT depends_on_id,device_id,ARRAY[depends_on_id,device_id],1 FROM fleet_demo.dependson
  UNION ALL
  SELECT w.root,d.device_id,w.path||d.device_id,w.depth+1
  FROM walk w JOIN fleet_demo.dependson d ON d.depends_on_id=w.dependent
  WHERE w.depth<4 AND NOT d.device_id=ANY(w.path)
)
SELECT root,count(DISTINCT dependent) AS dependents FROM walk
GROUP BY root HAVING count(DISTINCT dependent)>=3 ORDER BY dependents DESC,root;
