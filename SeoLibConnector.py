import requests

class SeoLibParser:
    def __init__(self, token):
        self.token = token
        self.headers = {
            "Content-Type":"application/json"
        }
    
    def check_code(self, response):
        if (response.status_code == requests.codes.ok):
            return response.json()
        else:
            return {"success": False, "status_code": response.status_code, "error": response.text}

    def get_projects(self):
        url = "https://api.seolib.ru/projects/list"
        payload = {
            "token": self.token
        }
        response = requests.post(url, json=payload, headers=self.headers)
        return self.check_code(response)
        
    def get_project_engines(self, project_id):
        url = "https://api.seolib.ru/projects/settings/engines"
        payload = {
            "token": self.token,
            "project": int(project_id)
        }
        response = requests.post(url, json=payload, headers=self.headers)
        return self.check_code(response)

    def get_project_regions(self, project_id, engine_id):
        url = "https://api.seolib.ru/projects/settings/engines/regions"
        payload = {
            "token": self.token,
            "project": int(project_id),
            "engine": int(engine_id)
        }
        response = requests.post(url, json=payload, headers=self.headers)
        return self.check_code(response)

    def get_report_positions(self, project_id, engine_id, region, period):
        url = "https://api.seolib.ru/projects/reports/positions"
        payload = {
            "token": self.token,
            "project": int(project_id),
            "engine": int(engine_id),
            "region": int(region),
            "period": period
        }
        response = requests.post(url, json=payload, headers=self.headers)
        return self.check_code(response)
    
    def generate_report(self, project_id, period):
        engines = self.get_project_engines(project_id)
        report = {}
        for engine in engines["content"]["engines"]:
            regions = self.get_project_regions(project_id, engine["engine"]["id"])
            region_report = {}
            for region in regions["content"]["regions"]:
                region_report[region["region"]["name"]] = self.get_report_positions(project_id, engine["engine"]["id"], region["region"]["id"], period)
            report[engine["engine"]["name"]] = region_report
        return report
                
                


token = ""
SLP = SeoLibParser(token)

projects = SLP.get_projects()
#print(projects)
print(SLP.generate_report(109142, ["2021-01-01", "2021-02-01"]))
