import os;
from os import chdir;
import csv;
import numpy;
from numpy import *;
from string import ascii_lowercase;
import eyed3;


current_dir = "/partage/Reves Party Playlist/Ambiances";
chdir(current_dir);


index_file_name="index_tags.csv";


for path, dirs, files in os.walk(current_dir):
    for filename in files:
        # On sélectionne ceux qui finissent par .tex
        if filename[-4:] in [".mp3",".aac","flac",".wav"]:
            afile = eyed3.load(os.path.join(path, filename));
            if afile is None:
                p.append([path,os.path.join(path, filename)]);
            else:
                if not(afile.tag is None):
                    if not(afile.tag.non_std_genre is None):
                        b = [i.capitalize() for i in afile.tag.non_std_genre.name.split(', ')]
                        c = ', '.join(b)
                        print(c)
                        afile.tag.genre = c
                        afile.tag.save();
