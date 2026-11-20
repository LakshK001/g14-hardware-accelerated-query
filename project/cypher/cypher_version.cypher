// Course Prerequisite Graph : Neo4j / Cypher version
// Run these in Neo4j Browser one block at a time.

// ---------- 0. CLEAN START (optional) ----------
MATCH (n) DETACH DELETE n;

// ---------- 1. CONSTRAINTS (like PRIMARY KEY / UNIQUE in SQL) ----------
CREATE CONSTRAINT course_code_unique IF NOT EXISTS
FOR (c:Course) REQUIRE c.code IS UNIQUE;

CREATE CONSTRAINT skill_name_unique IF NOT EXISTS
FOR (s:Skill) REQUIRE s.name IS UNIQUE;

// ---------- 2. CREATE NODES ----------
CREATE (:Course {code:'CS101', name:'Programming in C',                  credits:4, semester:1});
CREATE (:Course {code:'MA101', name:'Discrete Mathematics',             credits:3, semester:1});
CREATE (:Course {code:'MA102', name:'Probability and Statistics',       credits:3, semester:2});
CREATE (:Course {code:'CS102', name:'Data Structures',                  credits:4, semester:2});
CREATE (:Course {code:'CS201', name:'Design and Analysis of Algorithms',credits:4, semester:3});
CREATE (:Course {code:'CS202', name:'DBMS',                             credits:4, semester:4});
CREATE (:Course {code:'CS203', name:'Operating Systems',                credits:4, semester:4});
CREATE (:Course {code:'CS301', name:'Machine Learning',                 credits:3, semester:5});
CREATE (:Course {code:'CS302', name:'Advanced DBMS',                    credits:3, semester:6});
CREATE (:Course {code:'CS401', name:'Big Data Systems',                 credits:3, semester:7});

CREATE (:Skill {name:'C Programming'});
CREATE (:Skill {name:'Logic and Proofs'});
CREATE (:Skill {name:'Problem Solving'});
CREATE (:Skill {name:'Statistics'});
CREATE (:Skill {name:'SQL'});
CREATE (:Skill {name:'Process Management'});
CREATE (:Skill {name:'Model Building'});
CREATE (:Skill {name:'Query Optimization'});
CREATE (:Skill {name:'Distributed Processing'});

// ---------- 3. CREATE RELATIONSHIPS ----------
// (A)-[:REQUIRES]->(B)  means  course A needs course B first

UNWIND [
  ['CS102','CS101'], ['MA102','MA101'],
  ['CS201','CS102'], ['CS201','MA101'],
  ['CS202','CS102'], ['CS203','CS102'],
  ['CS301','CS201'], ['CS301','MA102'],
  ['CS302','CS202'], ['CS302','CS201'],
  ['CS401','CS302'], ['CS401','CS203']
] AS pair
MATCH (a:Course {code: pair[0]}), (b:Course {code: pair[1]})
CREATE (a)-[:REQUIRES]->(b);

UNWIND [
  ['CS101','C Programming'], ['CS101','Problem Solving'],
  ['MA101','Logic and Proofs'], ['MA102','Statistics'],
  ['CS102','Problem Solving'], ['CS201','Problem Solving'],
  ['CS202','SQL'], ['CS203','Process Management'],
  ['CS301','Model Building'], ['CS302','Query Optimization'],
  ['CS401','Distributed Processing']
] AS pair
MATCH (c:Course {code: pair[0]}), (s:Skill {name: pair[1]})
CREATE (c)-[:TEACHES]->(s);

// ---------- 4. QUERIES ----------

// Q1. Direct prerequisites of CS401
MATCH (:Course {code:'CS401'})-[:REQUIRES]->(p:Course)
RETURN p.code, p.name;

// Q2. ALL courses needed for CS401 (direct + indirect)
//     the * means "repeat this relationship any number of times"
MATCH (:Course {code:'CS401'})-[:REQUIRES*1..]->(p:Course)
RETURN DISTINCT p.code, p.name
ORDER BY p.code;

// Q2b. Same thing but also show how far each course is (level)
MATCH path = (:Course {code:'CS401'})-[:REQUIRES*1..]->(p:Course)
RETURN p.code, p.name, min(length(path)) AS level_no
ORDER BY level_no DESC, p.code;

// Q3. All skills gained after finishing everything needed for CS401
MATCH (:Course {code:'CS401'})-[:REQUIRES*1..]->(p:Course)-[:TEACHES]->(s:Skill)
RETURN DISTINCT s.name
ORDER BY s.name;

// Q4. Courses with no prerequisite
MATCH (c:Course)
WHERE NOT (c)-[:REQUIRES]->()
RETURN c.code, c.name;

// Q5. Which courses depend on CS102 (directly or indirectly)?
MATCH (c:Course)-[:REQUIRES*1..]->(:Course {code:'CS102'})
RETURN DISTINCT c.code, c.name
ORDER BY c.code;

// Q6. Show the whole graph picture for CS401 (click "graph" view in browser)
MATCH path = (:Course {code:'CS401'})-[:REQUIRES*1..]->(:Course)
RETURN path;
