"""
Disease Spread Network Analysis - Neo4j Graph Ingestion Script
==============================================================
Populates the Neo4j Graph Database with:
- Healthcare Facility nodes (Hospitals, Clinics, Polyclinics with GIS coordinates)
- Location nodes (Districts, States)
- Disease / Pathogen nodes (Syndromic categories, R0 transmission metrics)
- Outbreak Cluster nodes (Risk levels, Detection timestamps)
- Relational network edges:
  (:Facility)-[:LOCATED_IN]->(:Location)
  (:Facility)-[:PART_OF_CLUSTER]->(:Cluster)
  (:Facility)-[:REPORTS_OUTBREAK]->(:Disease)
  (:Disease)-[:SPREAD_TO]->(:Location)

Usage:
  python init_disease_spread_neo4j.py
"""

import os
import sys

CYPHER_SCRIPT = """
// 1. Uniqueness Constraints & Indexes
CREATE CONSTRAINT IF NOT EXISTS FOR (f:Facility) REQUIRE f.name IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (d:Disease) REQUIRE d.name IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (l:Location) REQUIRE l.district IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (c:Cluster) REQUIRE c.name IS UNIQUE;

// 2. Geographic Locations
MERGE (mumbai_city:Location {district: 'Mumbai City', state: 'Maharashtra', zone: 'South Central'});
MERGE (mumbai_sub:Location {district: 'Mumbai Suburban', state: 'Maharashtra', zone: 'North Central'});
MERGE (thane:Location {district: 'Thane', state: 'Maharashtra', zone: 'Metropolitan Fringe'});
MERGE (pune:Location {district: 'Pune', state: 'Maharashtra', zone: 'Western Ghats Corridor'});

// 3. Outbreak Cluster Nodes
MERGE (cluster:Cluster {
    name: 'Mumbai Respiratory Signal',
    risk_level: 'HIGH PRIORITY',
    confidence: 0.87,
    detected_date: '2026-08-16',
    intensity: '78%'
});

// 4. Healthcare Facilities
MERGE (kem:Facility {
    name: 'KEM Hospital Parel',
    type: 'Hospital',
    district: 'Mumbai City',
    latitude: 18.9986,
    longitude: 72.8436,
    cases_per_wk: 42,
    growth_rate: '+52%'
})
MERGE (kem)-[:LOCATED_IN]->(mumbai_city)
MERGE (kem)-[:PART_OF_CLUSTER {severity: 'High Hospital Load', trend: '+52%'}]->(cluster);

MERGE (sion:Facility {
    name: 'Sion Municipal Hospital',
    type: 'Hospital',
    district: 'Mumbai Suburban',
    latitude: 19.0356,
    longitude: 72.8601,
    cases_per_wk: 38,
    growth_rate: '+40%'
})
MERGE (sion)-[:LOCATED_IN]->(mumbai_sub)
MERGE (sion)-[:PART_OF_CLUSTER {severity: 'High Hospital Load', trend: '+40%'}]->(cluster);

MERGE (dadar:Facility {
    name: 'Dadar Central Clinic',
    type: 'Clinic',
    district: 'Mumbai City',
    latitude: 19.0178,
    longitude: 72.8478,
    cases_per_wk: 26,
    growth_rate: '+65%'
})
MERGE (dadar)-[:LOCATED_IN]->(mumbai_city)
MERGE (dadar)-[:PART_OF_CLUSTER {severity: 'Clinic Spike', trend: '+65%'}]->(cluster);

MERGE (kurla:Facility {
    name: 'Kurla West Polyclinic',
    type: 'Polyclinic',
    district: 'Mumbai Suburban',
    latitude: 19.0657,
    longitude: 72.8792,
    cases_per_wk: 19,
    growth_rate: '+35%'
})
MERGE (kurla)-[:LOCATED_IN]->(mumbai_sub)
MERGE (kurla)-[:PART_OF_CLUSTER {severity: 'Clinic Spike', trend: '+35%'}]->(cluster);

MERGE (bandra:Facility {
    name: 'Bandra Sentinel Center',
    type: 'Hospital',
    district: 'Mumbai Suburban',
    latitude: 19.0596,
    longitude: 72.8295,
    cases_per_wk: 14,
    growth_rate: 'Stable'
})
MERGE (bandra)-[:LOCATED_IN]->(mumbai_sub)
MERGE (bandra)-[:PART_OF_CLUSTER {severity: 'Monitoring', trend: 'Stable'}]->(cluster);

MERGE (thane_fac:Facility {
    name: 'Thane Civil Sentinel',
    type: 'Hospital',
    district: 'Thane',
    latitude: 19.1970,
    longitude: 72.9760,
    cases_per_wk: 12,
    growth_rate: 'Baseline'
})
MERGE (thane_fac)-[:LOCATED_IN]->(thane)
MERGE (thane_fac)-[:PART_OF_CLUSTER {severity: 'Monitoring', trend: 'Baseline'}]->(cluster);

MERGE (byculla:Facility {
    name: 'Byculla Municipal Dispensary',
    type: 'Clinic',
    district: 'Mumbai City',
    latitude: 18.9750,
    longitude: 72.8330,
    cases_per_wk: 20,
    growth_rate: '+45%'
})
MERGE (byculla)-[:LOCATED_IN]->(mumbai_city)
MERGE (byculla)-[:PART_OF_CLUSTER {severity: 'High Hospital Load', trend: '+45%'}]->(cluster);

// 5. Diseases & Surveillance Vectors
MERGE (resp:Disease {name: 'Acute Respiratory Infection', category: 'Respiratory', r0_estimate: 2.1});
MERGE (dengue:Disease {name: 'Dengue Fever', category: 'Vector-borne', r0_estimate: 1.8});
MERGE (gastro:Disease {name: 'Gastroenteritis', category: 'Gastrointestinal', r0_estimate: 1.4});

MERGE (kem)-[:REPORTS_OUTBREAK {date: '2026-08-16', cases: 42}]->(resp);
MERGE (sion)-[:REPORTS_OUTBREAK {date: '2026-08-16', cases: 38}]->(resp);
MERGE (dadar)-[:REPORTS_OUTBREAK {date: '2026-08-16', cases: 26}]->(resp);
MERGE (kurla)-[:REPORTS_OUTBREAK {date: '2026-08-16', cases: 19}]->(resp);
MERGE (byculla)-[:REPORTS_OUTBREAK {date: '2026-08-16', cases: 20}]->(resp);

MERGE (dadar)-[:REPORTS_OUTBREAK {date: '2026-08-16', cases: 18}]->(dengue);
MERGE (kurla)-[:REPORTS_OUTBREAK {date: '2026-08-16', cases: 14}]->(dengue);

// 6. Connect Disease Spatial Spread Paths
MERGE (resp)-[:SPREAD_TO {velocity_score: 0.88, transmission_vector: 'Airborne Droplets', weekly_growth: '+52%'}]->(mumbai_city);
MERGE (resp)-[:SPREAD_TO {velocity_score: 0.79, transmission_vector: 'Airborne Droplets', weekly_growth: '+40%'}]->(mumbai_sub);
MERGE (dengue)-[:SPREAD_TO {velocity_score: 0.65, transmission_vector: 'Aedes Mosquito Vector', weekly_growth: '+28%'}]->(mumbai_city);
"""

def main():
    print("=" * 70)
    print("Disease Spread Network Analysis - Neo4j Graph Initialization")
    print("=" * 70)
    
    neo4j_uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.environ.get("NEO4J_USER", "neo4j")
    neo4j_password = os.environ.get("NEO4J_PASSWORD", "neo4j")

    try:
        from neo4j import GraphDatabase
        print(f"Connecting to Neo4j at {neo4j_uri}...")
        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        with driver.session() as session:
            for statement in CYPHER_SCRIPT.strip().split(";"):
                stmt = statement.strip()
                if stmt:
                    session.run(stmt)
        print("Graph database populated successfully with Disease Spread Network data!")
        driver.close()
    except Exception as e:
        print(f"Note: Neo4j connection not active or driver not installed ({e}).")
        print("\nYou can directly copy-paste the Cypher script into Neo4j Browser:")
        print("-" * 70)
        print(CYPHER_SCRIPT)
        print("-" * 70)

if __name__ == "__main__":
    main()
