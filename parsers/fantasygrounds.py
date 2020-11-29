import os
import re
import uuid
import shutil

from xml.etree import ElementTree
from natsort import natsorted, humansorted
from parsers import Parser
from models import Group, Page, Map, Marker, Encounter, Combatant, Module
from slugify import slugify

import logging
logger = logging.getLogger(__name__)

# class helpers
class Image:
    tag = None
    name = None
    bitmap = None

class NPC:
    tag = None
    name = None

class FantasyGrounds(Parser):   

    def parse_xml(self, path, module):
        logger.debug("parsing xml: %s", path)

        # lookup tables
        lookup = {}
        lookup["encounter"] = {}
        lookup["page"] = {}
        lookup["map"] = {}
        lookup["image"] = {}
        lookup["npc"] = {}
        lookup["quest"] = {}

        # arrays
        pages = []
        maps = []
        groups = []
        encounters = []

        # xml tree
        tree = ElementTree.parse(path)
        root = tree.getroot()

        # NPCS
        logger.info("parsing npcs")

        for category in root.findall("./npc/category"):
            for node in category.findall("*"):
                tag = node.tag
                name = node.find("name").text
                
                npc = NPC()
                npc.name = name
                lookup["npc"][tag] = npc

        # PAGES
        logger.info("parsing pages")

        parent = Group()
        parent.name = "Story"
        parent.slug = slugify(parent.name)
        groups.append(parent)

        for category in root.findall("./encounter/category"):

            group = Group()
            group.name = category.get("name")
            group.slug = slugify(group.name)
            group.parent = parent

            if group.name == None or group.name == "":
                group = parent
            else:
                groups.append(group)

            # get all pages
            for node in category.findall("*"):
                # tag 
                tag = node.tag

                # create page
                page = Page()
                page.meta["tag"] = tag
                page.name = node.find("name").text
                page.slug = slugify(page.name)
                page.content = ElementTree.tostring(node.find("text"), encoding='utf-8', method='xml').decode('utf-8')
                page.parent = group

                pages.append(page)
                lookup["page"][tag] = page

        # QUESTS
        logger.info("parsing quests")

        parent = Group()
        parent.name = "Quests"
        parent.slug = slugify(parent.name)
        groups.append(parent)

        # some modules got, so use this instead
        for node in root.findall("./quest/*/*"):
        # for node in root.findall("./quest/*"):
            # tag 
            tag = node.tag

            # create quest
            page = Page()
            page.meta["tag"] = id
            page.name = node.find("name").text
            page.slug = slugify(page.name)

            page.content = ElementTree.tostring(node.find("description"), encoding='utf-8', method='xml').decode('utf-8')

            cr = node.find("cr").text if node.find("cr") else ""
            xp = node.find("xp").text if node.find("xp") else ""

            page.content += '<p><strong>CR:</strong> ' + cr + ' <strong>XP:</strong> ' + xp + '</p>'
            page.parent = parent

            pages.append(page)
            lookup["quest"][tag] = page

        # sort
        pages_sorted = humansorted(pages, key=lambda x: x.name)

        # MAPS & IMAGES
        logger.info("parsing images and maps")

        parent = Group()
        parent.name = "Maps & Images"
        parent.slug = slugify(parent.name)
        groups.append(parent)

        for category in root.findall("./image/category"):
            group = Group()
            group.name = category.get("name")
            group.slug = slugify(group.name)
            group.parent = parent

            if group.name == None or group.name == "":
                group = parent
            else:
                groups.append(group)

            for node in category.findall("*"):
                # tag 
                tag = node.tag

                # create image
                image = Image()
                image.tag = tag
                image.bitmap = node.find("./image/bitmap").text.replace("\\", "/")
                image.name = node.find("name").text
                
                lookup["image"][tag] = image

                markers = []

                # get shortcouts (markers)
                for shortcut in node.findall("./image/shortcuts/shortcut"):
                    # create marker
                    marker = Marker()
                    marker.x = shortcut.find("x").text
                    marker.y = shortcut.find("y").text

                    shortcut_ref = shortcut.find("recordname").text.replace("encounter.", "").replace("@*", "")
                    page = None
                    if shortcut_ref in lookup["page"]:
                        page = lookup["page"][shortcut_ref]

                        # remove chapter numbers from page name
                        # maybe use a regex?
                        name = page.name
                        if " " in page.name:
                             first, second = page.name.split(' ', 1)
                             if "." in first:
                                name = second

                        marker.name = name
                        marker.contentRef = "/page/" + page.slug

                    markers.append(marker)

                if markers or node.find("./image/gridsize") != None:
                    # if markers not empty, its a map
                    map = Map()
                    map.parent = group
                    map.meta["tag"] = tag
                    map.name = image.name
                    map.slug = slugify(map.name)
                    map.image = image.bitmap
                    if node.find("./image/gridsize") != None:
                        map.gridSize = node.find("./image/gridsize").text
                    if node.find("./image/gridoffset") != None:
                        gridOffset = node.find("./image/gridoffset").text
                        map.gridOffsetX = gridOffset.split(",")[0]
                        map.gridOffsetY = gridOffset.split(",")[1]
                    map.markers = markers

                    maps.append(map)
                    lookup["map"][tag] = map
                else:
                    # otherwise, its a image
                    page = Page()
                    page.parent = group
                    page.meta["tag"] = tag
                    page.name = image.name
                    page.slug = slugify(page.name)
                    page.content = '<p><img class="size-full" src="' + image.bitmap + '" /></p>'

                    pages_sorted.append(page)
                    # do not add to lookup tables

        # sort
        maps_sorted = humansorted(maps, key=lambda x: x.name)

        # ENCOUNTERS
        logger.info("parsing encounters")

        parent = Group()
        parent.name = "Encounters"
        parent.slug = slugify(parent.name)
        groups.append(parent)

        for category in root.findall("./battle/category"):
            group = Group()
            group.name = category.get("name")
            group.slug = slugify(group.name)
            group.parent = parent

            if group.name == None or group.name == "":
                group = parent
            else:
                groups.append(group)

            for node in category.findall("*"):
                # tag
                tag = node.tag

                # create encounter
                encounter = Encounter()
                encounter.meta["tag"] = tag
                encounter.parent = group

                encounter.name = node.find("name").text
                encounter.slug = slugify(encounter.name)
                
                encounters.append(encounter)
                lookup["encounter"][tag] = encounter

                # get combatants
                for npcnode in node.find("npclist").findall("*"):

                    # get positions
                    maplinks = npcnode.findall("./maplink/*")

                    # combatants count
                    count = int(npcnode.find("count").text)

                    # iterate
                    for x in range(count):
                        combatant = Combatant()
                        combatant.name = npcnode.find("name").text
                        encounter.combatants.append(combatant)

                        # if position on map
                        if len(maplinks) == count:
                            maplinknode = maplinks[x]

                            if maplinknode.find("./imagex") != None:
                                combatant.x = maplinknode.find("./imagex").text

                            if maplinknode.find("./imagey") != None:
                                combatant.y = maplinknode.find("./imagey").text



        encounters_sorted = humansorted(encounters, key=lambda x: x.name)

        # custom regex for processing links
        def href_replace(match):
            key = str(match.group(2)).split("@")[0]

            type = match.group(1)

            if type == "image" and key in lookup["map"]:
                return 'href="/map/' + lookup["map"][key].slug
            elif type == "image" and key in lookup["image"]:
                return 'href="' + lookup["image"][key].bitmap
            elif type == "encounter" and key in lookup["page"]:
                return 'href="' + lookup["page"][key].slug
            elif type == "battle" and key in lookup["encounter"]:
                return 'href="/encounter/' + lookup["encounter"][key].slug
            elif type == "quest" and key in lookup["quest"]:
                return 'href="' + lookup["quest"][key].slug
            else:
                return key

        # fix content tags in pages
        for page in pages_sorted:
            content = page.content
            # maybe regex 
            content = content.replace('<text type="formattedtext">', '').replace('<text>', '').replace('</text>', '')
            content = content.replace('<description type="formattedtext">', '').replace('<description>', '').replace('</description>', '')
            content = content.replace('<frame>', '<blockquote class="read">').replace('</frame>', '</blockquote>')
            content = content.replace('<frameid>DM</frameid>', '')
            content = content.replace('\r', '<br />')
            content = content.replace('<h>', '<h3>').replace('</h>', '</h3>')
            content = content.replace('<list>', '<ul>').replace('</list>', '</ul>')
            # content = content.replace("<linklist>", "<ul>").replace("</linklist>", "</ul>")
            content = content.replace('<linklist>', '').replace('</linklist>', '')
            content = content.replace('<link', '<p><a').replace('</link>', '</a></p>')
            content = content.replace(' recordname', ' href')
            content = content.strip()

            # fix links
            content = re.sub(r'href=[\'"]?(encounter|battle|image|quest)\.([^\'">]+)', href_replace, content)

            # add title
            if content.startswith('<h3>'):
                page.content = content.replace('<h3>', '<h2>', 1).replace('</h3>', '</h2>', 1)
            else:
                page.content = '<h2>' + page.name + '</h2>' + content

        # assign data to module
        module.groups = groups
        module.pages = pages_sorted
        module.maps = maps_sorted
        module.encounters = encounters_sorted

        return module

    def process_mod(self, path, module):
        # path info
        basename = os.path.basename(path)
        dirname = os.path.dirname(path)
        unpacked_dir = os.path.join(dirname, module.slug)

        # unpack archive
        logger.info("unpacking archive: %s", basename)
        shutil.unpack_archive(path, unpacked_dir, "zip")

        # convert db.xml to module.xml
        xml_file = os.path.join(unpacked_dir, "db.xml")
        if os.path.exists(xml_file):
            # parse data
            self.parse_xml(xml_file, module)

            # create dst
            dst = os.path.join(unpacked_dir, "module.xml")

            # export xml
            module.export_xml(dst)

        else:
           raise ValueError("db.xml not found")

        # create archive
        Module.create_archive(unpacked_dir, module.slug)

        return module


    def process(self, path, module):
        # path info
        basename = os.path.basename(path)
        ext = os.path.splitext(basename)[1]

        # file check
        if os.path.isfile(path) == False:
            raise ValueError('Path must be a file')

        # extension check
        if ext == ".mod":
            # .mod file
            self.process_mod(path, module)
        elif ext == ".xml":
            # .xml file
            self.parse_xml(path, module)
        else:  
            raise ValueError('Invalid path') 

