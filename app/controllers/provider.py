import json
import re
import requests
from requests import Session
from bs4 import BeautifulSoup
from models.clase import Clase
from enum import Enum
from models.user import User
from log import logger
from typing import List
from datetime import datetime
from urllib.parse import urlencode


class Provider:

    DOMAIN = "https://www.beprogrammer.site/beprogrammer"
    LOGIN = f"{DOMAIN}/miportal"
    CLASES = f"{DOMAIN}/clases/sede/13"
    PROFILE = f"{DOMAIN}/clientes/perfil_usuarios"
    HOME = f"{DOMAIN}/welcome"
    SCHEDULE = f"{DOMAIN}/clientes/asesorias"

    def __init__(self):
        self.session = None

    def __make_get_request(self, url):
        if not self.session:
            raise Exception("No se ha autenticado")
        res = self.session.get(url)
        logger.info(f"[{res.status_code}] {url}")
        return res.content
    
    def autenticate(self, code):
        with Session() as session:
            res = session.post(self.LOGIN, data={
                "username": code,
                "password": code
            })
            if not res.ok:
                print("Error logging in")
                return
            
            self.session = session
            self.code = code
            return self

    def get_scheduled_classes(self, id) -> list[Clase]:
        content = self.__make_get_request(f"{self.SCHEDULE}/{id}")
        soup = BeautifulSoup(content, "html.parser")

        script = soup.find_all("script")[7]

        script_content = script.string

        match = re.search(r'events\:\s(\[[\s\S]*?\])', script_content)
        regex = r'''(?<=[}\]"']),(?!\s*[{["'])'''

        try:
            found = match.group(1).replace("'", '"')
            found = found.replace("id:", '"id":')
            found = found.replace("title:", '"title":')
            found = found.replace("start:", '"start":')
            found = found.replace("url:", '"url":')
            found = found.replace("color:", '"color":')
            found = found.replace('"VIRTUAL  | KIDS"', 'VIRTUAL  | KIDS"')
            result = re.sub(regex, "", found, 0)
            
            classes = []

            for item in json.loads(result):
                item["start"] = datetime.strptime(item["start"], '%Y-%m-%dT%H:%M')
                clase = Clase(**item)
                classes.append(clase)
            return classes
        except Exception as e:
            print("Error parsing JSON:", e)
            return []

    def get_clases(self) -> List[Clase]:
        content = self.__make_get_request(self.CLASES)
        soup = BeautifulSoup(content, "html.parser")

        script = soup.find_all("script")[7]

        script_content = script.string

        match = re.search(r'events\:\s(\[[\s\S]*?\])', script_content)
        regex = r'''(?<=[}\]"']),(?!\s*[{["'])'''

        try:
            found = match.group(1).replace("'", '"')
            found = found.replace("id:", '"id":')
            found = found.replace("title:", '"title":')
            found = found.replace("start:", '"start":')
            found = found.replace("url:", '"url":')
            found = found.replace("color:", '"color":')
            found = found.replace('"VIRTUAL  | KIDS"', 'VIRTUAL  | KIDS"')
            result = re.sub(regex, "", found, 0)
            
            classes = []

            for item in json.loads(result):
                item["start"] = datetime.strptime(item["start"], '%Y-%m-%dT%H:%M')
                clase = Clase(**item)
                classes.append(clase)
            return classes
        except Exception as e:
            print("Error parsing JSON:", e)
            return []
        

    def get_profile(self) -> User:
        try:
            content = self.__make_get_request(self.HOME)
            
            # Se obtiene el id del usuario
            soup = BeautifulSoup(content, "html.parser")
            elem = soup.find_all("a", attrs={"class": "nav-link"})[1]
            id = elem.attrs.get("href").split("?")[0].split("/")[-1]

            # Se accede a la pagina de perfil del usuario con el id anterior para obtener la info del usuario
            content = self.__make_get_request(f"{self.PROFILE}/{id}")
            soup = BeautifulSoup(content, "html.parser")
            values = soup.find_all("p", attrs={"class": "t-orange"})
            
            info = [value.text for value in values]
            dates = info[3].split("  ")

            level = soup.find("option").text

            user = User(**{
                "id": id,
                "name": info[0].upper(),
                "code": info[1].upper(),
                "since": dates[0],
                "until": dates[1],
                "profile": level.upper()
            })

            return user
        except:
            raise Exception("El usuario no existe")
    
    def get_class_link(self, url):
        content = self.__make_get_request(url)
        soup = BeautifulSoup(content, "html.parser")
        links = soup.find_all("a")
        for link in links:
            if "meet.google.com" in link.attrs["href"]:
                return link.attrs["href"]
        return ""
    
    def get_attendance(self):
        user = self.get_profile()
        content = self.__make_get_request(f"{self.PROFILE}/{user.id}")
        soup = BeautifulSoup(content, "html.parser")
        filas = soup.find_all("tbody")[1].find_all("tr")
        output = []
        for fila in filas:
            th = fila.find("th")
            tds = fila.find_all("td")
            item = {
                "class": th.text,
                "start": tds[0].text,
                "status": tds[1].text,
                "observation": tds[2].text,
            }

            output.append(item)
            
        return output
    
    def send_program_request(self, url, data: dict):
        encoded_data=urlencode(data)

        res = self.session.post(url, data=encoded_data, headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://www.beprogrammer.site",
            "Referer": url,
            "Autority": "www.beprogrammer.site",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "es-US,es-419;q=0.9,es;q=0.8,en;q=0.7",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
        })
        self.session.get(res.url)
        return res
    
    def create_soup(self, url):
        content = self.session.get(url).content
        return BeautifulSoup(content, "html.parser")
        
    @property
    def cookies(self):
        if self.session:
            return self.session.cookies.get_dict()
        return None