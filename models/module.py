import uuid
import logging
import shutil
import os
from xml.etree import ElementTree

from models import Group, Page, Map, Marker, Encounter, Combatant
from slugify import slugify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Module:

    def __init__(self):

        self.id = str(uuid.uuid4())
        self.name = "Unknown module"
        self.slug = "unknown-module"
        self.description = None
        self.author = None
        self.code = None
        self.category = None
        self.image = None

        self.groups = []
        self.pages = []
        self.maps = []
        self.encounters = []

    def export_xml(self, path):
    
        # create module
        module = ElementTree.Element("module")
        
        module.set("id", self.id)
        ElementTree.SubElement(module, "name").text = self.name
        ElementTree.SubElement(module, "slug").text = self.slug

        if self.description:
            ElementTree.SubElement(module, "description").text = self.description

        if self.author:
            ElementTree.SubElement(module, "author").text = self.author

        if self.code:
            ElementTree.SubElement(module, "code").text = self.code

        if self.category:
            ElementTree.SubElement(module, "category").text = self.category

        if self.image:
            ElementTree.SubElement(module, "image").text = self.image

        # groups
        for group in self.groups:
            el = ElementTree.SubElement(module, "group")
            el.set("id", group.id)

            if group.parent != None:
                el.set("parent", group.parent.id)

            ElementTree.SubElement(el, "name").text = group.name
            ElementTree.SubElement(el, "slug").text = group.slug

        # pages
        for page in self.pages:
            el = ElementTree.SubElement(module, "page")
            el.set("id", page.id)
            
            if page.parent != None:
                el.set("parent", page.parent.id)

            ElementTree.SubElement(el, "name").text = page.name
            ElementTree.SubElement(el, "slug").text = page.slug
            ElementTree.SubElement(el, "content").text = page.content

        # maps
        for map in self.maps:
            
            el = ElementTree.SubElement(module, "map")
            el.set("id", map.id)
            
            if map.parent != None:
                el.set("parent", map.parent.id)

            ElementTree.SubElement(el, "name").text = map.name
            ElementTree.SubElement(el, "slug").text = map.slug

            if map.image:
                ElementTree.SubElement(el, "image").text = map.image

            if map.gridSize:
                ElementTree.SubElement(el, "gridSize").text = map.gridSize

            if map.gridOffsetX:
                ElementTree.SubElement(el, "gridOffsetX").text = map.gridOffsetX

            if map.gridOffsetY:
                ElementTree.SubElement(el, "gridOffsetY").text = map.gridOffsetY

            # markers
            for marker in map.markers:
                markerElement = ElementTree.SubElement(el, "marker")
                if marker.name:
                    ElementTree.SubElement(markerElement, "name").text = marker.name

                if marker.label:
                    ElementTree.SubElement(markerElement, "label").text = marker.label

                if marker.shape:
                    ElementTree.SubElement(markerElement, "shape").text = marker.shape

                if marker.color:
                    ElementTree.SubElement(markerElement, "color").text = marker.color
                
                if marker.x:
                    ElementTree.SubElement(markerElement, "x").text = marker.x

                if marker.y: 
                    ElementTree.SubElement(markerElement, "y").text = marker.y

                if marker.contentRef: 
                    contentElement = ElementTree.SubElement(markerElement, "content")
                    contentElement.set("ref", marker.contentRef)

                if marker.locked:
                    ElementTree.SubElement(markerElement, "locked").text = marker.locked

                if marker.hidden:
                    ElementTree.SubElement(markerElement, "hidden").text = marker.hidden

        # encounters
        for encounter in self.encounters:
            
            el = ElementTree.SubElement(module, "encounter")
            el.set("id", encounter.id)
            
            if encounter.parent != None:
                el.set("parent", encounter.parent.id)

            ElementTree.SubElement(el, "name").text = encounter.name
            ElementTree.SubElement(el, "slug").text = encounter.slug

            # combatants
            for combatant in encounter.combatants:
                combatantElement = ElementTree.SubElement(el, "combatant")
                if combatant.name:
                    ElementTree.SubElement(combatantElement, "name").text = combatant.name

                if combatant.label:  
                    ElementTree.SubElement(combatantElement, "label").text = combatant.label

                if combatant.role:
                    ElementTree.SubElement(combatantElement, "role").text = combatant.role

                if combatant.name:
                    ElementTree.SubElement(combatantElement, "name").text = combatant.name

                if combatant.x and combatant.x != "0":
                    ElementTree.SubElement(combatantElement, "x").text = combatant.x

                if combatant.y and combatant.y != "0":
                    ElementTree.SubElement(combatantElement, "y").text = combatant.y

                if combatant.monsterRef:
                    monsterElement = ElementTree.SubElement(combatantElement, "monster")
                    monsterElement.set("ref", combatant.monsterRef)
                
        tree = ElementTree.ElementTree(module)
        tree.write(path, encoding="utf-8", xml_declaration=True)

    def create_archive(src, name):
        # copy assets
        logger.debug("copying assets")
        current_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        assets_src = os.path.join(current_dir, "assets")
        assets_dst = os.path.join(src, "assets")

        # remove exising assets dir
        if os.path.exists(assets_dst):
            shutil.rmtree(assets_dst)

        # copy assets
        shutil.copytree(assets_src, assets_dst)

        # create archive
        logger.info("creating archive")
        parent_dir = os.path.dirname(src)
        archive_file = os.path.join(parent_dir, name)

        shutil.make_archive(archive_file, 'zip', src)

        # rename
        os.rename(archive_file + ".zip",  archive_file + ".module")