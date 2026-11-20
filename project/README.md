# DBMS Mini Project · Course Prerequisite Graph

Models university course prerequisites as a graph and answers questions such as
"which courses must I finish before *Big Data Systems*?", in two ways:

- **Neo4j / Cypher** (graph database): variable-length paths such as `-[:REQUIRES*1..]->`
- **SQL** (relational): a recursive CTE (`WITH RECURSIVE`)

The same data and queries are written in both, so the two approaches can be compared side by side.

**Team:** Krish (25124053), Krish Singhal (25124054), Laksh Kapoor (25124055), Lucky (25124056)
B.Tech IT, Dr B R Ambedkar National Institute of Technology Jalandhar · Subject: DBMS

## Folder layout

```
project/
├── report/
│   └── DBMS_Mini_Project_Course_Prerequisite_Graph.pdf   # full project report
├── sql/
│   └── sql_version.sql          # tables, data and queries (MySQL 8 / PostgreSQL / SQLite)
└── cypher/
    └── cypher_version.cypher    # constraints, nodes, relationships and queries (Neo4j)
```

## Data model

| | SQL | Neo4j |
|---|---|---|
| Courses | `course` table | `(:Course)` nodes |
| Skills | `skill` table | `(:Skill)` nodes |
| Prerequisites | `prerequisite` table (many-to-many) | `(:Course)-[:REQUIRES]->(:Course)` |
| Skills taught | `course_skill` table | `(:Course)-[:TEACHES]->(:Skill)` |

The sample data has 10 courses, 9 skills and 12 prerequisite links.

## Queries

| # | Question | SQL | Cypher |
|---|---|---|---|
| Q1 | Direct prerequisites of CS401 | JOIN | 1-hop `MATCH` |
| Q2 | All prerequisites of CS401 (direct and indirect), with depth | recursive CTE | `[:REQUIRES*1..]` |
| Q3 | All skills gained on the way to CS401 | recursive CTE + JOIN | path + `[:TEACHES]` |
| Q4 | Courses with no prerequisite | `NOT IN` | `WHERE NOT (c)-[:REQUIRES]->()` |
| Q5 | Courses that depend on CS102 | reverse recursive CTE | reverse path |
| Q6 | Graph picture of CS401's prerequisites | – | `RETURN path` (graph view) |

## How to run

**SQL:** run `sql/sql_version.sql` in MySQL 8, PostgreSQL or SQLite, for example:

```bash
sqlite3 :memory: < sql/sql_version.sql
```

**Neo4j:** open Neo4j Browser (Neo4j Desktop, Community or Aura) and run `cypher/cypher_version.cypher`
one block at a time. The first block (`MATCH (n) DETACH DELETE n`) clears the database, so use an empty one.

## Expected results (checked by running the SQL file)

| Query | Result |
|---|---|
| Q1 | CS203, CS302 |
| Q2 | CS101, MA101, CS102, CS201, CS202, CS203, CS302 (7 courses) |
| Q3 | C Programming, Logic and Proofs, Problem Solving, Process Management, Query Optimization, SQL |
| Q4 | CS101, MA101 |
| Q5 | CS201, CS202, CS203, CS301, CS302, CS401 |
