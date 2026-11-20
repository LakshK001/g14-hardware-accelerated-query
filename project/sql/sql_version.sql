-- Course Prerequisite Graph : SQL version (works in MySQL 8, PostgreSQL, SQLite)
-- Subject: DBMS

-- ---------- 1. TABLES ----------

CREATE TABLE course (
    course_code  VARCHAR(10)  PRIMARY KEY,
    course_name  VARCHAR(60)  NOT NULL,
    credits      INT          NOT NULL CHECK (credits > 0),
    semester     INT          NOT NULL CHECK (semester BETWEEN 1 AND 8)
);

CREATE TABLE skill (
    skill_id     INT          PRIMARY KEY,
    skill_name   VARCHAR(40)  NOT NULL UNIQUE
);

-- many-to-many: a course can have many prerequisites, and a course
-- can be a prerequisite of many courses
CREATE TABLE prerequisite (
    course_code  VARCHAR(10)  NOT NULL,
    prereq_code  VARCHAR(10)  NOT NULL,
    PRIMARY KEY (course_code, prereq_code),
    FOREIGN KEY (course_code) REFERENCES course(course_code),
    FOREIGN KEY (prereq_code) REFERENCES course(course_code),
    CHECK (course_code <> prereq_code)
);

-- many-to-many: a course teaches many skills, a skill is taught in many courses
CREATE TABLE course_skill (
    course_code  VARCHAR(10)  NOT NULL,
    skill_id     INT          NOT NULL,
    PRIMARY KEY (course_code, skill_id),
    FOREIGN KEY (course_code) REFERENCES course(course_code),
    FOREIGN KEY (skill_id)    REFERENCES skill(skill_id)
);

CREATE INDEX idx_prereq_course ON prerequisite(course_code);

-- ---------- 2. DATA ----------

INSERT INTO course VALUES ('CS101', 'Programming in C',           4, 1);
INSERT INTO course VALUES ('MA101', 'Discrete Mathematics',      3, 1);
INSERT INTO course VALUES ('MA102', 'Probability and Statistics',3, 2);
INSERT INTO course VALUES ('CS102', 'Data Structures',           4, 2);
INSERT INTO course VALUES ('CS201', 'Design and Analysis of Algorithms', 4, 3);
INSERT INTO course VALUES ('CS202', 'DBMS',                      4, 4);
INSERT INTO course VALUES ('CS203', 'Operating Systems',         4, 4);
INSERT INTO course VALUES ('CS301', 'Machine Learning',          3, 5);
INSERT INTO course VALUES ('CS302', 'Advanced DBMS',             3, 6);
INSERT INTO course VALUES ('CS401', 'Big Data Systems',          3, 7);

INSERT INTO skill VALUES (1, 'C Programming');
INSERT INTO skill VALUES (2, 'Logic and Proofs');
INSERT INTO skill VALUES (3, 'Problem Solving');
INSERT INTO skill VALUES (4, 'Statistics');
INSERT INTO skill VALUES (5, 'SQL');
INSERT INTO skill VALUES (6, 'Process Management');
INSERT INTO skill VALUES (7, 'Model Building');
INSERT INTO skill VALUES (8, 'Query Optimization');
INSERT INTO skill VALUES (9, 'Distributed Processing');

-- prerequisite(course, its prerequisite)
INSERT INTO prerequisite VALUES ('CS102', 'CS101');
INSERT INTO prerequisite VALUES ('MA102', 'MA101');
INSERT INTO prerequisite VALUES ('CS201', 'CS102');
INSERT INTO prerequisite VALUES ('CS201', 'MA101');
INSERT INTO prerequisite VALUES ('CS202', 'CS102');
INSERT INTO prerequisite VALUES ('CS203', 'CS102');
INSERT INTO prerequisite VALUES ('CS301', 'CS201');
INSERT INTO prerequisite VALUES ('CS301', 'MA102');
INSERT INTO prerequisite VALUES ('CS302', 'CS202');
INSERT INTO prerequisite VALUES ('CS302', 'CS201');
INSERT INTO prerequisite VALUES ('CS401', 'CS302');
INSERT INTO prerequisite VALUES ('CS401', 'CS203');

INSERT INTO course_skill VALUES ('CS101', 1);
INSERT INTO course_skill VALUES ('CS101', 3);
INSERT INTO course_skill VALUES ('MA101', 2);
INSERT INTO course_skill VALUES ('MA102', 4);
INSERT INTO course_skill VALUES ('CS102', 3);
INSERT INTO course_skill VALUES ('CS201', 3);
INSERT INTO course_skill VALUES ('CS202', 5);
INSERT INTO course_skill VALUES ('CS203', 6);
INSERT INTO course_skill VALUES ('CS301', 7);
INSERT INTO course_skill VALUES ('CS302', 8);
INSERT INTO course_skill VALUES ('CS401', 9);

-- ---------- 3. QUERIES ----------

-- Q1. Direct prerequisites of CS401 (simple JOIN)
SELECT c.course_code, c.course_name
FROM prerequisite p
JOIN course c ON c.course_code = p.prereq_code
WHERE p.course_code = 'CS401';

-- Q2. ALL courses needed for CS401 (direct + indirect) using recursive CTE
WITH RECURSIVE needed(course_code, level_no) AS (
    -- starting point: direct prerequisites of the target
    SELECT prereq_code, 1
    FROM prerequisite
    WHERE course_code = 'CS401'

    UNION ALL

    -- keep going: prerequisites of the courses found so far
    SELECT p.prereq_code, n.level_no + 1
    FROM prerequisite p
    JOIN needed n ON p.course_code = n.course_code
)
SELECT c.course_code, c.course_name, MIN(n.level_no) AS level_no
FROM needed n
JOIN course c ON c.course_code = n.course_code
GROUP BY c.course_code, c.course_name
ORDER BY level_no DESC, c.course_code;

-- Q3. All skills a student gets after finishing everything needed for CS401
WITH RECURSIVE needed(course_code) AS (
    SELECT prereq_code FROM prerequisite WHERE course_code = 'CS401'
    UNION
    SELECT p.prereq_code
    FROM prerequisite p
    JOIN needed n ON p.course_code = n.course_code
)
SELECT DISTINCT s.skill_name
FROM needed n
JOIN course_skill cs ON cs.course_code = n.course_code
JOIN skill s         ON s.skill_id = cs.skill_id
ORDER BY s.skill_name;

-- Q4. Courses that have no prerequisite (can be taken first)
SELECT course_code, course_name
FROM course
WHERE course_code NOT IN (SELECT course_code FROM prerequisite);

-- Q5. Which courses depend on CS102 (directly or indirectly)?
WITH RECURSIVE dependents(course_code) AS (
    SELECT course_code FROM prerequisite WHERE prereq_code = 'CS102'
    UNION
    SELECT p.course_code
    FROM prerequisite p
    JOIN dependents d ON p.prereq_code = d.course_code
)
SELECT c.course_code, c.course_name
FROM dependents d
JOIN course c ON c.course_code = d.course_code
ORDER BY c.course_code;
