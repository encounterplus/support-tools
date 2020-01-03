#!/usr/local/bin/python3
import os
import sys
import json
import math
import uuid
import requests
import tempfile
import shutil
import re
import base64
from json import JSONDecodeError

def getJSON(theurl):
	rawjson = ""
	if theurl.startswith("https://www.dndbeyond.com/"):
		#Pretend to be firefox
		user_agent = "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:70.0) Gecko/20100101 Firefox/70.0"
		headers = {'User-Agent': user_agent}
		urlcomponents = theurl.split("/")
		charid = urlcomponents[-1]
		if charid == "json":
			charid = urlcomponents[-2]
		url = "https://www.dndbeyond.com/character/{}/json".format(charid)
		response = requests.get(url,headers=headers)
		if response.status_code != 200:
			print (theurl)
			print ("Could not download this character from D&D Beyond: {}".format(response.status_code))
			print ("Make sure the character is public")
			return
		else:
			if "character" in response.json():
				character = response.json()["character"]
			else:
				character = response.json()
			return character
	else:
		print ("This is not a url for D&D Beyond: {}".format(theurl))
		return

def genXML(character):	
	level = 0
	characterXML = "\t<player>\n"
	characterXML += "\t\t<name>{}</name>\n".format(character["name"])
	#characterXML += "\t\t<slug>ddb-{}</slug>\n".format(character["id"])
	if len(character["classes"]) > 1:
		allclasses = []
		for cclass in character["classes"]:
			level += cclass["level"]
			allclasses.append("{} {}".format(cclass["definition"]["name"],cclass["level"]))
		characterXML += "\t\t<class>{}</class>\n".format('/'.join(allclasses))
	else:
		characterclass = character["classes"][0]["definition"]["name"]
		level = character["classes"][0]["level"]
		characterXML += "\t\t<class>{}</class>\n".format(characterclass)
	characterXML += "\t\t<level>{}</level>\n".format(level)
	characterXML += "\t\t<xp>{}</xp>\n".format(character["currentXp"])
	hitpoints = character["baseHitPoints"]
	armorclass = 0
	stat_str = character["stats"][0]["value"]
	stat_dex = character["stats"][1]["value"]
	stat_con = character["stats"][2]["value"]
	stat_int = character["stats"][3]["value"]
	stat_wis = character["stats"][4]["value"]
	stat_cha = character["stats"][5]["value"]
	race = character["race"]["fullName"]
	speed = character["race"]["weightSpeeds"]["normal"]["walk"]
	modifiers = character["modifiers"]
	senses = []
	for modifier in (modifiers["race"]+modifiers["class"]+modifiers["background"]+modifiers["item"]+modifiers["feat"]+modifiers["condition"]):
		if modifier["isGranted"] == True and modifier["type"].lower() == "bonus":
			if modifier["subType"].lower() == "strength-score":
				stat_str += modifier["value"]
			elif modifier["subType"].lower() == "dexterity-score":
				stat_dex += modifier["value"]
			elif modifier["subType"].lower() == "constitution-score":
				stat_con += modifier["value"]
			elif modifier["subType"].lower() == "inteligence-score":
				stat_int += modifier["value"]
			elif modifier["subType"].lower() == "wisdom-score":
				stat_wis += modifier["value"]
			elif modifier["subType"].lower() == "charisma-score":
				stat_cha += modifier["value"]
	
	hitpoints += math.floor((stat_con - 10)/2)*level
	initiative = math.floor((stat_dex - 10)/2)
	equipment = []
	for equip in character["inventory"]:
#		for i in range(equip["quantity"]):
#			equipment.append(equip["definition"]["name"])
#		if equip["quantity"] > 1:
#			equipment.append("{} (x{:d})".format(equip["definition"]["name"],equip["quantity"]))
#		else:
#			equipment.append(equip["definition"]["name"])
		equipment.append(equip["definition"]["name"])
		if equip["equipped"] == True and "armorClass" in equip["definition"]:
			armorclass += equip["definition"]["armorClass"]
	if armorclass == 0:
		armorclass = 10
	armorclass += math.floor((stat_dex - 10)/2)
	light = ""
	languages = []
	resistence = []
	immunity = []
	skill = {}
	str_save = math.floor((stat_str - 10)/2)
	skill["Athletics"] = str_save
	dex_save = math.floor((stat_dex - 10)/2)
	skill["Acrobatics"] = dex_save
	skill["Sleight of Hand"] = dex_save
	skill["Stealth"] = dex_save
	con_save = math.floor((stat_con - 10)/2)
	int_save = math.floor((stat_int - 10)/2)
	skill["Arcana"] = int_save
	skill["History"] = int_save
	skill["Investigation"] = int_save
	skill["Nature"] = int_save
	skill["Religion"] = int_save
	wis_save = math.floor((stat_wis - 10)/2)
	skill["Animal Handling"] = wis_save
	skill["Insight"] = wis_save
	skill["Medicine"] = wis_save
	skill["Perception"] = wis_save
	skill["Survival"] = wis_save
	cha_save = math.floor((stat_cha - 10)/2)
	skill["Deception"] = cha_save
	skill["Intimidation"] = cha_save
	skill["Performance"] = cha_save
	skill["Persuasion"] = cha_save
	for modifier in (modifiers["race"]+modifiers["class"]+modifiers["background"]+modifiers["item"]+modifiers["feat"]+modifiers["condition"]):
		if modifier["type"].lower() == "half-proficiency":
			bonus = math.ceil(((level/4)+1)/2)
			if modifier["subType"].lower() == "athletics" or modifier["subType"].lower() == "ability-checks":
				skill["Athletics"] = math.floor((stat_str - 10)/2) + bonus
			if modifier["subType"].lower() == "acrobatics" or modifier["subType"].lower() == "ability-checks":
				skill["Acrobatics"] = math.floor((stat_dex - 10)/2) + bonus
			if modifier["subType"].lower() == "sleight-of-hand" or modifier["subType"].lower() == "ability-checks":
				skill["Sleight of Hand"] = math.floor((stat_dex - 10)/2) + bonus
			if modifier["subType"].lower() == "stealth" or modifier["subType"].lower() == "ability-checks":
				skill["Stealth"] = math.floor((stat_dex - 10)/2) + bonus
			if modifier["subType"].lower() == "arcana" or modifier["subType"].lower() == "ability-checks":
				skill["Arcana"] = math.floor((stat_int - 10)/2) + bonus
			if modifier["subType"].lower() == "history" or modifier["subType"].lower() == "ability-checks":
				skill["History"] = math.floor((stat_int - 10)/2) + bonus
			if modifier["subType"].lower() == "investigation" or modifier["subType"].lower() == "ability-checks":
				skill["Investigation"] = math.floor((stat_int - 10)/2) + bonus
			if modifier["subType"].lower() == "nature" or modifier["subType"].lower() == "ability-checks":
				skill["Nature"] = math.floor((stat_int - 10)/2) + bonus
			if modifier["subType"].lower() == "religion" or modifier["subType"].lower() == "ability-checks":
				skill["Religion"] = math.floor((stat_int - 10)/2) + bonus
			if modifier["subType"].lower() == "animal-handling" or modifier["subType"].lower() == "ability-checks":
				skill["Animal Handling"] = math.floor((stat_wis - 10)/2) + bonus
			if modifier["subType"].lower() == "insight" or modifier["subType"].lower() == "ability-checks":
				skill["Insight"] = math.floor((stat_wis - 10)/2) + bonus
			if modifier["subType"].lower() == "medicine" or modifier["subType"].lower() == "ability-checks":
				skill["Medicine"] = math.floor((stat_wis - 10)/2) + bonus
			if modifier["subType"].lower() == "perception" or modifier["subType"].lower() == "ability-checks":
				skill["Perception"] = math.floor((stat_wis - 10)/2) + bonus
			if modifier["subType"].lower() == "survival" or modifier["subType"].lower() == "ability-checks":
				skill["Survival"] = math.floor((stat_wis - 10)/2) + bonus
			if modifier["subType"].lower() == "deception" or modifier["subType"].lower() == "ability-checks":
				skill["Deception"] = math.floor((stat_cha - 10)/2) + bonus
			if modifier["subType"].lower() == "intimidation" or modifier["subType"].lower() == "ability-checks":
				skill["Intimidation"] = math.floor((stat_cha - 10)/2) + bonus
			if modifier["subType"].lower() == "performance" or modifier["subType"].lower() == "ability-checks":
				skill["Performance"] = math.floor((stat_cha - 10)/2) + bonus
			if modifier["subType"].lower() == "persuasion" or modifier["subType"].lower() == "ability-checks":
				skill["Persuasion"] = math.floor((stat_cha - 10)/2) + bonus
			if modifier["subType"].lower() == "initiative":
				initiative = math.floor((stat_dex - 10)/2) + bonus
			if modifier["subType"].lower() == "strength-saving-throws":
				str_save = math.floor((stat_str - 10)/2) + bonus
			if modifier["subType"].lower() == "dexterity-saving-throws":
				dex_save = math.floor((stat_dex - 10)/2) + bonus
			if modifier["subType"].lower() == "constitution-saving-throws":
				con_save = math.floor((stat_con - 10)/2) + bonus
			if modifier["subType"].lower() == "inteligence-saving-throws":
				int_save = math.floor((stat_int - 10)/2) + bonus
			if modifier["subType"].lower() == "wisdom-saving-throws":
				wis_save = math.floor((stat_wis - 10)/2) + bonus
			if modifier["subType"].lower() == "charisma-saving-throws":
				cha_save = math.floor((stat_cha - 10)/2) + bonus
	for modifier in (modifiers["race"]+modifiers["class"]+modifiers["background"]+modifiers["item"]+modifiers["feat"]+modifiers["condition"]):
		if modifier["type"].lower() == "proficiency":
			bonus = math.ceil((level/4)+1)
			if modifier["subType"].lower() == "athletics" or modifier["subType"].lower() == "ability-checks":
				skill["Athletics"] = math.floor((stat_str - 10)/2) + bonus
			if modifier["subType"].lower() == "acrobatics" or modifier["subType"].lower() == "ability-checks":
				skill["Acrobatics"] = math.floor((stat_dex - 10)/2) + bonus
			if modifier["subType"].lower() == "sleight-of-hand" or modifier["subType"].lower() == "ability-checks":
				skill["Sleight of Hand"] = math.floor((stat_dex - 10)/2) + bonus
			if modifier["subType"].lower() == "stealth" or modifier["subType"].lower() == "ability-checks":
				skill["Stealth"] = math.floor((stat_dex - 10)/2) + bonus
			if modifier["subType"].lower() == "arcana" or modifier["subType"].lower() == "ability-checks":
				skill["Arcana"] = math.floor((stat_int - 10)/2) + bonus
			if modifier["subType"].lower() == "history" or modifier["subType"].lower() == "ability-checks":
				skill["History"] = math.floor((stat_int - 10)/2) + bonus
			if modifier["subType"].lower() == "investigation" or modifier["subType"].lower() == "ability-checks":
				skill["Investigation"] = math.floor((stat_int - 10)/2) + bonus
			if modifier["subType"].lower() == "nature" or modifier["subType"].lower() == "ability-checks":
				skill["Nature"] = math.floor((stat_int - 10)/2) + bonus
			if modifier["subType"].lower() == "religion" or modifier["subType"].lower() == "ability-checks":
				skill["Religion"] = math.floor((stat_int - 10)/2) + bonus
			if modifier["subType"].lower() == "animal-handling" or modifier["subType"].lower() == "ability-checks":
				skill["Animal Handling"] = math.floor((stat_wis - 10)/2) + bonus
			if modifier["subType"].lower() == "insight" or modifier["subType"].lower() == "ability-checks":
				skill["Insight"] = math.floor((stat_wis - 10)/2) + bonus
			if modifier["subType"].lower() == "medicine" or modifier["subType"].lower() == "ability-checks":
				skill["Medicine"] = math.floor((stat_wis - 10)/2) + bonus
			if modifier["subType"].lower() == "perception" or modifier["subType"].lower() == "ability-checks":
				skill["Perception"] = math.floor((stat_wis - 10)/2) + bonus
			if modifier["subType"].lower() == "survival" or modifier["subType"].lower() == "ability-checks":
				skill["Survival"] = math.floor((stat_wis - 10)/2) + bonus
			if modifier["subType"].lower() == "deception" or modifier["subType"].lower() == "ability-checks":
				skill["Deception"] = math.floor((stat_cha - 10)/2) + bonus
			if modifier["subType"].lower() == "intimidation" or modifier["subType"].lower() == "ability-checks":
				skill["Intimidation"] = math.floor((stat_cha - 10)/2) + bonus
			if modifier["subType"].lower() == "performance" or modifier["subType"].lower() == "ability-checks":
				skill["Performance"] = math.floor((stat_cha - 10)/2) + bonus
			if modifier["subType"].lower() == "persuasion" or modifier["subType"].lower() == "ability-checks":
				skill["Persuasion"] = math.floor((stat_cha - 10)/2) + bonus
			if modifier["subType"].lower() == "initiative":
				initiative = math.floor((stat_dex - 10)/2) + bonus
			if modifier["subType"].lower() == "strength-saving-throws":
				str_save = math.floor((stat_str - 10)/2) + bonus
			if modifier["subType"].lower() == "dexterity-saving-throws":
				dex_save = math.floor((stat_dex - 10)/2) + bonus
			if modifier["subType"].lower() == "constitution-saving-throws":
				con_save = math.floor((stat_con - 10)/2) + bonus
			if modifier["subType"].lower() == "inteligence-saving-throws":
				int_save = math.floor((stat_int - 10)/2) + bonus
			if modifier["subType"].lower() == "wisdom-saving-throws":
				wis_save = math.floor((stat_wis - 10)/2) + bonus
			if modifier["subType"].lower() == "charisma-saving-throws":
				cha_save = math.floor((stat_cha - 10)/2) + bonus
	for modifier in (modifiers["race"]+modifiers["class"]+modifiers["background"]+modifiers["item"]+modifiers["feat"]+modifiers["condition"]):
		if modifier["type"].lower() == "expertise":
			bonus = math.ceil(((level/4)+1)*2)
			if modifier["subType"].lower() == "athletics" or modifier["subType"].lower() == "ability-checks":
				skill["Athletics"] = math.floor((stat_str - 10)/2) + bonus
			if modifier["subType"].lower() == "acrobatics" or modifier["subType"].lower() == "ability-checks":
				skill["Acrobatics"] = math.floor((stat_dex - 10)/2) + bonus
			if modifier["subType"].lower() == "sleight-of-hand" or modifier["subType"].lower() == "ability-checks":
				skill["Sleight of Hand"] = math.floor((stat_dex - 10)/2) + bonus
			if modifier["subType"].lower() == "stealth" or modifier["subType"].lower() == "ability-checks":
				skill["Stealth"] = math.floor((stat_dex - 10)/2) + bonus
			if modifier["subType"].lower() == "arcana" or modifier["subType"].lower() == "ability-checks":
				skill["Arcana"] = math.floor((stat_int - 10)/2) + bonus
			if modifier["subType"].lower() == "history" or modifier["subType"].lower() == "ability-checks":
				skill["History"] = math.floor((stat_int - 10)/2) + bonus
			if modifier["subType"].lower() == "investigation" or modifier["subType"].lower() == "ability-checks":
				skill["Investigation"] = math.floor((stat_int - 10)/2) + bonus
			if modifier["subType"].lower() == "nature" or modifier["subType"].lower() == "ability-checks":
				skill["Nature"] = math.floor((stat_int - 10)/2) + bonus
			if modifier["subType"].lower() == "religion" or modifier["subType"].lower() == "ability-checks":
				skill["Religion"] = math.floor((stat_int - 10)/2) + bonus
			if modifier["subType"].lower() == "animal-handling" or modifier["subType"].lower() == "ability-checks":
				skill["Animal Handling"] = math.floor((stat_wis - 10)/2) + bonus
			if modifier["subType"].lower() == "insight" or modifier["subType"].lower() == "ability-checks":
				skill["Insight"] = math.floor((stat_wis - 10)/2) + bonus
			if modifier["subType"].lower() == "medicine" or modifier["subType"].lower() == "ability-checks":
				skill["Medicine"] = math.floor((stat_wis - 10)/2) + bonus
			if modifier["subType"].lower() == "perception" or modifier["subType"].lower() == "ability-checks":
				skill["Perception"] = math.floor((stat_wis - 10)/2) + bonus
			if modifier["subType"].lower() == "survival" or modifier["subType"].lower() == "ability-checks":
				skill["Survival"] = math.floor((stat_wis - 10)/2) + bonus
			if modifier["subType"].lower() == "deception" or modifier["subType"].lower() == "ability-checks":
				skill["Deception"] = math.floor((stat_cha - 10)/2) + bonus
			if modifier["subType"].lower() == "intimidation" or modifier["subType"].lower() == "ability-checks":
				skill["Intimidation"] = math.floor((stat_cha - 10)/2) + bonus
			if modifier["subType"].lower() == "performance" or modifier["subType"].lower() == "ability-checks":
				skill["Performance"] = math.floor((stat_cha - 10)/2) + bonus
			if modifier["subType"].lower() == "persuasion" or modifier["subType"].lower() == "ability-checks":
				skill["Persuasion"] = math.floor((stat_cha - 10)/2) + bonus
			if modifier["subType"].lower() == "initiative":
				initiative = math.floor((stat_dex - 10)/2) + bonus
			if modifier["subType"].lower() == "strength-saving-throws":
				str_save = math.floor((stat_str - 10)/2) + bonus
			if modifier["subType"].lower() == "dexterity-saving-throws":
				dex_save = math.floor((stat_dex - 10)/2) + bonus
			if modifier["subType"].lower() == "constitution-saving-throws":
				con_save = math.floor((stat_con - 10)/2) + bonus
			if modifier["subType"].lower() == "inteligence-saving-throws":
				int_save = math.floor((stat_int - 10)/2) + bonus
			if modifier["subType"].lower() == "wisdom-saving-throws":
				wis_save = math.floor((stat_wis - 10)/2) + bonus
			if modifier["subType"].lower() == "charisma-saving-throws":
				cha_save = math.floor((stat_cha - 10)/2) + bonus
	for modifier in (modifiers["race"]+modifiers["class"]+modifiers["background"]+modifiers["item"]+modifiers["feat"]+modifiers["condition"]):
		if modifier["type"].lower() == "set" and modifier["subType"].lower() == "unarmored-armor-class":
			if modifier["statId"] == 3:
				armorclass += math.floor((stat_con - 10)/2)
			if modifier["value"] is not None:
				armorclass += modifier["value"]
		if modifier["type"].lower() == "ignore" and modifier["subType"].lower() == "unarmored-dex-ac-bonus":
			armorclass -= math.floor((stat_dex - 10)/2)
		if modifier["type"].lower() == "set-base" and modifier["subType"].lower() == "darkvision":
			senses.append("{} {} ft.".format(modifier["subType"].lower(),modifier["value"]))
			light = "\t\t<light id=\"{}\">\n\t\t\t<enabled>YES</enabled>\n\t\t\t<radiusMin>0</radiusMin>\n\t\t\t<radiusMax>{}</radiusMax>\n\t\t\t<color>#ffffff</color>\n\t\t\t<opacity>0.5</opacity>\n\t\t\t<alwaysVisible>YES</alwaysVisible>\n\t\t</light>\n".format(uuid.uuid4(),modifier["value"])
		if modifier["type"].lower() == "language":
			languages.append(modifier["friendlySubtypeName"])
		if modifier["type"].lower() == "resistance":
			resistence.append(modifier["friendlySubtypeName"])
		if modifier["type"].lower() == "immunity":
			immunity.append(modifier["friendlySubtypeName"])
	spells = []
	for spell in character["spells"]["race"]:
		spells.append(spell["definition"]["name"])
	for spell in character["spells"]["class"]:
		spells.append(spell["definition"]["name"])
	for spell in character["spells"]["item"]:
		spells.append(spell["definition"]["name"])
	for spell in character["spells"]["feat"]:
		spells.append(spell["definition"]["name"])
	for classsp in character["classSpells"]:
		for spell in classsp["spells"]:
			spells.append(spell["definition"]["name"])
	party = ""
	if "campaign" in character and character["campaign"] is not None:
		party = character["campaign"]["name"]
	background = ""
	if "background" in character and character["background"] is not None and character["background"]["definition"] is not None:
		background = character["background"]["definition"]["name"]
		bg_def = character["background"]["definition"]
	feats = []
	for feat in character["feats"]:
		feats.append(feat["definition"]["name"])
		feat_def = feat["definition"]
	personality = character["traits"]["personalityTraits"]
	bonds = character["traits"]["bonds"]
	ideals = character["traits"]["ideals"]
	flaws = character["traits"]["flaws"]
	appearance = character["traits"]["appearance"]
	characterXML += "\t\t<race>{}</race>\n".format(race)
	characterXML += "\t\t<initiative>{}</initiative>\n".format(initiative)
	characterXML += "\t\t<ac>{}</ac>\n".format(armorclass)
	characterXML += "\t\t<hp>{}</hp>\n".format(hitpoints)
	characterXML += "\t\t<speed>{}</speed>\n".format(speed)
	characterXML += "\t\t<str>{}</str>\n".format(stat_str)
	characterXML += "\t\t<dex>{}</dex>\n".format(stat_dex)
	characterXML += "\t\t<con>{}</con>\n".format(stat_con)
	characterXML += "\t\t<int>{}</int>\n".format(stat_int)
	characterXML += "\t\t<wis>{}</wis>\n".format(stat_wis)
	characterXML += "\t\t<cha>{}</cha>\n".format(stat_cha)
	characterXML += "\t\t<desc>{}</desc>\n".format(appearance)
	characterXML += "\t\t<party>{}</party>\n".format(party)
	characterXML += "\t\t<faction>{}</faction>\n".format("")
	characterXML += "\t\t<passive>{}</passive>\n".format(skill["Perception"]+10)
	characterXML += "\t\t<spells>{}</spells>\n".format(", ".join(spells))
	characterXML += "\t\t<senses>{}</senses>\n".format(", ".join(senses))
	characterXML += "\t\t<languages>{}</languages>\n".format(", ".join(languages))
	characterXML += "\t\t<equipment>{}</equipment>\n".format(", ".join(equipment))
	characterXML += "\t\t<image>{}</image>\n".format(character["avatarUrl"].split('/')[-1])
	characterXML += "\t\t<personality>{}</personality>\n".format(personality)
	characterXML += "\t\t<ideals>{}</ideals>\n".format(ideals)
	characterXML += "\t\t<bonds>{}</bonds>\n".format(bonds)
	characterXML += "\t\t<flaws>{}</flaws>\n".format(flaws)
	skills = []
	for sk in sorted(skill.keys()):
		skills.append("{} {:+d}".format(sk,skill[sk]))
	characterXML += "\t\t<skill>{}</skill>\n".format(", ".join(skills))
	characterXML += "\t\t<save>Str {:+d}, Dex {:+d}, Con {:+d}, Int {:+d}, Wis {:+d}, Cha {:+d}</save>\n".format(str_save,dex_save,con_save,int_save,wis_save,cha_save)
	characterXML += "\t\t<resist>{}</resist>\n".format(", ".join(resistence))
	characterXML += "\t\t<immune>{}</immune>\n".format(", ".join(immunity))
	characterXML += "\t\t<background>{}</background>\n".format(background)
	characterXML += "\t\t<feats>{}</feats>\n".format(", ".join(feats))
	if light != "":
		characterXML += light
	characterXML += "\t</player>\n"
	return characterXML

def findURLS(fp):
	fp.seek(0, 0)
	characters = []
	regex = re.compile("<a[^>]*href=\"(/profile/.*/[0-9]+)\"[^>]*class=\"ddb-campaigns-character-card-header-upper-details-link\"[^>]*>")
	for line in fp:
		m = regex.search(line)
		if m:
			characterurl = m.group(1)
			if not characterurl.startswith("https://www.dndbeyond.com/"):
				characters.append("https://www.dndbeyond.com"+characterurl)
			else:
				characters.append(characterurl)
	return characters

def main():
	tempdir = tempfile.mkdtemp(prefix="ddbtoxml_")
	comependiumxml = os.path.join(tempdir, "compendium.xml")
	playersdir = os.path.join(tempdir, "players")
	os.mkdir(playersdir)
	with open(comependiumxml,mode='a',encoding='utf-8') as comependium:
		comependium.write("<?xml version=\"1.0\" encoding=\"utf-8\" standalone=\"no\"?>\n<compendium>\n")
	args = sys.argv
	if len(args) == 2 and args[1].startswith("--campaign"):
		regex = re.compile("<a[^>]*href=\"(/profile/.*/[0-9]+)\"[^>]*class=\"ddb-campaigns-character-card-header-upper-details-link\"[^>]*>")
		if args[1] == "--campaign":
			readin = sys.stdin
		elif os.path.isfile(args[1][11:]):
			readin = open(args[1][11:],'r')
		else:
			readin = base64.b64decode(args[1][11:]).decode("utf-8").splitlines()
		args = [sys.argv[0]]
		for line in readin:
			m = regex.search(line)
			if m:
				characterurl = m.group(1)
				if not characterurl.startswith("https://www.dndbeyond.com/"):
					args.append("https://www.dndbeyond.com"+characterurl)
				else:
					args.append(characterurl)
		try:
			readin.close()
		except:
			pass
	characters = []
	for i in range(len(args)):
		if args[i] == __file__:
			continue
		if os.path.isfile(args[i]):
				with open(args[i]) as infile:
					try:
						json.load(infile)
						characters.append(args[i])
					except JSONDecodeError:
						found = findURLS(infile)
						characters.extend(found)
		else:
			characters.append(args[i])
	if len(characters) == 0:
		characters.append("-")
	for i in range(len(characters)):
		if  characters[i] == '-' or os.path.isfile(characters[i]):
			if os.path.isfile(characters[i]):
				with open(characters[i],"r") as jsonfile:
					charjson = json.loads(jsonfile.read())
			else:
				charjson = json.loads(sys.stdin.read())
			if "character" in charjson:
				character = charjson["character"]
			else:
				character = charjson
		else:
			character = getJSON(characters[i])
		if character is not None:
			xmloutput = genXML(character)
			with open(comependiumxml,mode='a',encoding='utf-8') as comependium:
				comependium.write(xmloutput)
			if character["avatarUrl"] != "":
				local_filename = os.path.join(playersdir,character["avatarUrl"].split('/')[-1])
				r = requests.get(character["avatarUrl"], stream=True)
				if r.status_code == 200:
					with open(local_filename, 'wb') as f:
						for chunk in r.iter_content(chunk_size=8192):
							f.write(chunk)
	with open(comependiumxml,mode='a',encoding='utf-8') as comependium:
		comependium.write("</compendium>")

	zipfile = shutil.make_archive("ddbxml","zip",tempdir)
	os.rename(zipfile,os.path.join(os.getcwd(),"ddbxml.compendium"))
	zipfile = os.path.join(os.getcwd(),"ddbxml.compendium")
	try:
		import console
		console.open_in (zipfile)
	except ImportError:
		print(zipfile)

	try:
		shutil.rmtree(tempdir)
	except:
		print("Warning: error trying to delete the temporal directory:", file=sys.stderr)
		print(traceback.format_exc(), file=sys.stderr)

if __name__== "__main__":
	main()
