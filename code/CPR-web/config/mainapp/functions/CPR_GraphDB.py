import logging

from neo4j import GraphDatabase, RoutingControl
from neo4j.exceptions import DriverError, Neo4jError


class CPR_GraphDB:

    def __init__(self, uri, user, password, database=None):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database

    def close(self):
        # Don't forget to close the driver connection when you are finished
        # with it
        self.driver.close()

    def fetch_data(self, query, parameters):
        with self.driver.session() as session:  # 세션을 생성하고 자동으로 종료되게 함
            result = session.run(query, parameters)  # 쿼리 실행
            data = [record for record in result]  # 결과를 리스트로 변환
            return data
        
    def find_similar_job(self, user_skills):
        names = self._find_and_return_job(user_skills)
        return names

    def _find_and_return_job(self, user_skills):
        query = (
            "WITH $userSkills AS userSkills "
            "MATCH (skill:NCS)-[:HAS_JOB]->(job:KECO) "
            "WHERE skill.name IN userSkills "
            "WITH job, COUNT(skill) as matchCount "
            "ORDER BY matchCount DESC "
            "LIMIT 20 "
            "RETURN job"
        )
        
        parameters = {"userSkills": user_skills}
        
        jobs = self.fetch_data(query, parameters)
        data = [record['job']['name'] for record in jobs]

        return data
    
    def find_max_edge_skill(self, job_name):
        max_edge_skill = self._find_and_return_max_edge_skill(job_name)
        return max_edge_skill

    def _find_and_return_max_edge_skill(self, job_name):
        query = (
            "MATCH (keco:KECO {name: $job_name}) " # 직업 찾기
            "MATCH (ncs:NCS)-[:HAS_JOB]->(keco) " # 해당 직업 skill 찾기
            "WITH ncs, count(*) as connections " # skill 노드 간선 개수 count
            "ORDER BY connections DESC " # 간선 개수 내림차순으로 정렬
            #"LIMIT 5 "
            "RETURN ncs"
        )
        parameters={"job_name": job_name}
        
        result = self.fetch_data(query, parameters)
        data = [record['ncs']['name'] for record in result]  # 결과를 리스트로 변환

        return data
    
    def find_job(self, skill):
        query = (
            "MATCH (ncs:NCS {name: $skill}) " # 스킬 찾기
            "MATCH (keco:KECO)-[:HAS_JOB]->(ncs) " # 해당 스킬 관련 직업 찾기
            "WITH keco, count(*) as connections " # 직업 노드 간선 개수 count
            "ORDER BY connections DESC " # 간선 개수 내림차순으로 정렬
            #"LIMIT 5 "
            "RETURN keco"
        )
        parameters={"skill": skill}
        
        result = self.fetch_data(query, parameters)
        data = [record['keco']['name'] for record in result]  # 결과를 리스트로 변환

        return data
    
    def add_data(self, job_name, new_skill):
        query = (
            "MERGE (keco:KECO {name: $job_name}) " # 직업 찾기
            "MERGE (ncs:NCS {name: $new_skill}) " # 스킬 없으면 추가
            "MERGE (keco)-[:HAS_JOB]->(ncs) " # 양방향 관계 추가
            "MERGE (ncs)-[:HAS_JOB]->(keco) " # 양방향 관계 추가
        )
        parameters={"job_name": job_name, "new_skill": new_skill}
        
        self.fetch_data(query, parameters)

    def delete_data(self, job_name, skill):
        query = (
            "MATCH (keco:KECO {name: $job_name})-[r:HAS_JOB]-(ncs:NCS {name: $skill}) " # 관계 찾기
            "DELETE r " # 관계 삭제
        )
        parameters={"job_name": job_name, "skill": skill}
        
        self.fetch_data(query, parameters)

    
def openApp():
    scheme = "neo4j"  # Connecting to Aura, use the "neo4j+s" URI scheme
    host_name = "localhost"
    port = 7687
    uri = f"{scheme}://{host_name}:{port}"
    user = "neo4j"
    password = "cpr2024@"
    database = "neo4j"
    app = CPR_GraphDB(uri, user, password, database)
    return app

def getSimilarJob(user_skills):
    app = openApp()
    jobs = app.find_similar_job(user_skills)
    app.close()
    return jobs

def getSkills(job_name):
    app = openApp()
    skills = app.find_max_edge_skill(job_name)
    app.close()
    return skills

def getJobs(user_skills):
    app = openApp()
    jobs = app.find_job(user_skills)
    app.close()
    return jobs

def addData(job_name, new_skill):
    app = openApp()
    app.add_data(job_name, new_skill)
    app.close()

def deleteData(job_name, skill):
    app = openApp()
    app.delete_data(job_name, skill)
    app.close()