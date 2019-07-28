#! /usr/bin/python3
# -*- coding: utf-8 -*-

#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston MA 02110-1301, USA.
#
"""Les classes de donnees associees a la PAF board. Tourne sous Python 3.4

Auteur: PAF Fournie
Date: 21-06-2019
"""




import os;
from os import chdir;
import eyed3;


class bibliotheque:
    """Classe definie par:
    - le chemin du repertoire
    - les morceaux regroupes sous forme d'un dictionnaire avec
        pour clef, le nom du genre
        pour valeurs la liste des morceaux du genre en question"""
    def __init__(self, chemin):
        self.chemin = chemin
        self.contenu = {}
        for path, dirs, files in os.walk(chemin):
            for filename in files:
                # On sélectionne ceux qui sont des fichiers audio
                if filename[-4:] in [".mp3",".aac","flac",".wav",".m4a"]:
                    filepath=os.path.join(path, filename)
                    afile = eyed3.load(filepath)                    
                    if not(afile is None):
                        if not(afile.tag is None):
                            if not(afile.tag.genre is None):
                                track = morceau(filepath)
                                for l in afile.tag.non_std_genre.name.split(', '):
                                    if not(l in self.contenu):
                                        self.contenu.update({l:[track]})
                                    else:
                                        self.contenu[l].append(track)
    def __del__(self):
        del self.contenu



class morceau:
    """Classe definie par:
    - le chemin du fichier
    - la possibilite
        de jouer() le morceau
        de l'arreter()
        de le mettre en pause()"""
    def __init__(self, chemin):
        self.chemin = chemin
        self.afile = eyed3.load(chemin)
        self.artist = None
        self.track = None
        self.album = None
        self.genre = None
        if not(self.afile is None):
            if not(self.afile.tag is None):
                if not(self.afile.tag.artist is None):
                    self.artist = self.afile.tag.artist
                if not(self.afile.tag.title is None):
                    self.track = self.afile.tag.title
                if not(self.afile.tag.album is None):
                    self.album = self.afile.tag.album
                if not(self.afile.tag.non_std_genre is None):
                    if not(self.afile.tag.non_std_genre.name is None):
                        self.genre = self.afile.tag.non_std_genre.name
        
    def __repr__(self):
        return "Morceau: {} \nArtiste: {}\nAlbum: {}".format(
                self.track, self.artist, self.album)


    # on a besoin de lower than pour le tri
    def __lt__(self, other):
        return self.track < other.track
        
