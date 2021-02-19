import requests
import pandas as pd

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
                
def form_table(SLP, period):
    project_table = pd.DataFrame(columns=["project_id", "project_name", "project_domain"])
    engine_table = pd.DataFrame(columns=["engine_id", "engine_name"])
    region_table = pd.DataFrame(columns=["region_id", "region_name"])
    report_table = pd.DataFrame(columns=["date", "project_id", "engine_id", "region_id", "keyword", "position"])

    for project in SLP.get_projects()["content"]["projects"]:
        project_table = project_table.append({"project_id": project["id"], "project_name": project["name"], "project_domain": project["domain"]}, ignore_index=True)

        for engine in SLP.get_project_engines(project["id"])["content"]["engines"]:
            engine_table = engine_table.append({"engine_id": engine["engine"]["id"], "engine_name": engine["engine"]["name"]}, ignore_index=True)

            for region in SLP.get_project_regions(project["id"], engine["engine"]["id"])["content"]["regions"]:
                region_table = region_table.append({"region_id": region["region"]["id"], "region_name": region["region"]["name"]}, ignore_index=True)

                reports = SLP.get_report_positions(project["id"], engine["engine"]["id"], region["region"]["id"], period)
                
                if reports["success"]:
                    rep_count = len(reports["content"]["reports"])
                    i = 1
                    for report in reports["content"]["reports"]:
                        report_table = report_table.append(
                        {
                            "date": report["created"]["date"].split(" ")[0], 
                            "project_id": report["project"]["id"], 
                            "engine_id": report["engine"]["id"],
                            "region_id": report["region"]["id"],
                            "keyword": report["keyword"]["name"],
                            "position": report["data"]["position"]
                        }, ignore_index=True)
                        print("{}/{}".format(i, rep_count))
                        i += 1
    return project_table, engine_table.drop_duplicates().reset_index(drop=True), region_table.drop_duplicates().reset_index(drop=True), report_table


token = ""
SLP = SeoLibParser(token)

projects = SLP.get_projects()
#print(projects)
#print(SLP.generate_report(109142, ["2021-01-01", "2021-02-01"]))
p_t, e_t, reg_t, rep_t = form_table(SLP, ["2021-01-01/2021-02-01"])
print(rep_t)
