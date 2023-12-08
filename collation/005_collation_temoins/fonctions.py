#!usr/bin/env python
# -*- coding: utf-8 -*-

#import des librairies nécessaires
from lxml import etree
from xml.etree import ElementTree as et
from collatex import *
import json
import graphviz
import re
from prettytable import PrettyTable
from textwrap import fill

#défintion de la transformation vers du json
def XMLtoJson(id,xmlInput):
    # converts an XML tokenised and annotated input to JSON for collation
    witness = {}
    witness['id'] = id
    monXSL = etree.XML('''
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    exclude-result-prefixes="xs"
    version="1.0">

    <xsl:output method="text"/>

    <xsl:template match="/">
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="w">
        <xsl:text>{"text": "</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>", "i": "</xsl:text>
        <xsl:value-of select="@xml:id"/>
        <xsl:text>", "t": "</xsl:text>
        <xsl:value-of select="@lemma"/>
        <xsl:text>", "pos": "</xsl:text>
        <xsl:value-of select="@pos"/>
        <xsl:text>"}</xsl:text>
        <xsl:if test="following::w">
            <xsl:text>, </xsl:text>
        </xsl:if>
    </xsl:template>
</xsl:stylesheet>
    ''')
    monXSL = etree.XSLT(monXSL)
    witness['tokens'] = json.loads( '[' +str(monXSL(xmlInput)) +']')
    return witness

#définition de l'export qui nous convient
def notre_export_xml(table):
    readings = []
    for column in table.columns:
        app = et.Element('app')
        for key, value in sorted(column.tokens_per_witness.items()):
            child = et.Element('rdg')
            child.attrib['wit'] = "#" + key
            #modif ici pour garder tous les éléments de nos mots
            for item in value:
                child.attrib['xml:id'] = item.token_data["i"]
                child.attrib['lemma']= item.token_data["t"]
                child.attrib['pos'] = item.token_data["pos"]
                #fin modif
            child.text = "".join(str(item.token_data["text"]) for item in value)
            app.append(child)
        # Without the encoding specification, outputs bytes instead of a string
        result = et.tostring(app, encoding="unicode")
        readings.append(result)
    return "".join(readings)
    
#redéfintion de l'export des tables, sur les tokens directement et belles
def notretable(table):
    # print the table vertically
    x = PrettyTable()
    x.hrules = 1
    for row in table.rows:
        t_list = [(token.token_data["text"] for token in cell) if cell else ["-"] for cell in row.cells]
        x.add_column(row.header, [fill("".join(item), 20) for item in t_list])
    return x

