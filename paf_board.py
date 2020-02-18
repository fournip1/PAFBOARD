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
"""La PAF board. Tourne sous Python 3.5. Testee sous Debian 4.9.0-6-amd64 uniquement.
Permet de generer une music board a partir des genres des morceaux d'un repertoire choisi.
On peut associer plusieurs genres a un morceau a condition de les delimiter par ', '.
Auteur: PAF Fournie
Date: 21-06-2019
"""

import vlc
import gestion_morceaux as gm
import tkinter
from tkinter import font as tkfont
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
from threading import Thread, Event
import time
import os

class ttkTimer(Thread):
    """a class serving same function as wxTimer... but there may be better ways to do this
    """
    def __init__(self, callback, tick):
        Thread.__init__(self)
        self.callback = callback
        self.stopFlag = Event()
        self.tick = tick
        self.iters = 0

    def run(self):
        while not self.stopFlag.wait(self.tick):
            self.iters += 1
            self.callback()

    def stop(self):
        self.stopFlag.set()

    def get(self):
        return self.iters

    
class paf_board(tkinter.Tk):    
    def __init__(self,parent):
        tkinter.Tk.__init__(self,parent)
        self.parent = parent
        self.dirpath = None
        self.contenu = None
        self.clefs = None
        self.swindow = None
        self.onglets = None
        self.board = None
        self.boardactive = False
        self.player = None
        self.vlcplayer = None
        self.vlci = None
        self.seltracks = None
        self.Media = None
        self.pause  = None
        self.play   = None
        self.stop   = None
        self.back   = None
        
        self.screensize = [self.winfo_screenwidth(), self.winfo_screenheight()]
        self.bb = gm.bibliotheque

        # taille du board en %, puis position du board en %
        self.board_geometry_pc = [90,90,5,5]

        # conversion en paramtre de geometrie
        self.board_geometry = [int(self.board_geometry_pc[0]*self.screensize[0]/100),
                               int(self.board_geometry_pc[1]*self.screensize[1]/100),
                               int(self.board_geometry_pc[2]*self.screensize[0]/100),
                               int(self.board_geometry_pc[3]*self.screensize[1]/100)]

        
        self.nb_cols = 8
        self.buttonpolicesize = int(self.board_geometry[0]/(self.nb_cols*10))

        self.grid()
        # print(tkfont.families())

# sur la grille on place:
#       - le bouton de selection du repertoire a cote duquel on note le chemin du repertoire
#       - le bouton de generation du board

        self.filebutton = tkinter.Button(self,text=u"Selection du repertoire",
                                command=self.OnFileButtonClick)
        self.filebutton.grid(column=0,row=0)
        self.filebutton.bind("<Return>", self.OnPressEnter)

                
        self.chemin = tkinter.StringVar()
        self.label = tkinter.Label(self,textvariable=self.chemin,
                              anchor="w",fg="white",bg="blue")
        
        self.label.grid(column=1,row=0,sticky='EW')
        self.chemin.set(u"Chemin du repertoire")

        self.genbutton = tkinter.Button(self,text=u"Generer le board",
                                command=self.OnGenButtonClick,state='disabled')
        self.genbutton.grid(column=0,columnspan=1,row=1)        

# je sais pas trop a quoi ca sert. j'ai pompe le code :)
        self.grid_columnconfigure(0,weight=1)
        self.resizable(True,False)

# update, ca permet de mettre a jour les changements
        self.update()




    def CreateBoard(self):
# on cree la fenetre fille ou se trouve la board et le player
        self.swindow = tkinter.Toplevel(self)        
        self.swindow.wm_title("Votre PAF board")
        self.swindow.geometry("{}x{}+{}+{}".format(self.board_geometry[0],self.board_geometry[1],self.board_geometry[2],self.board_geometry[3]))
        self.swindow.resizable(True,True)
        
        # si on ferme cette fenetre fille
        self.swindow.protocol("WM_DELETE_WINDOW", self.CloseBoard)

        
# la classe Notebook permet d'obtenir les onglets

        # onglets, c'est le classeur contenant les onglets
        self.onglets = ttk.Notebook(self.swindow)

        
        
        self.board = tkinter.Frame(self.onglets)
        self.player = tkinter.Frame(self.onglets)
        self.onglets.add(self.board, text="La PAF board")
        self.onglets.add(self.player, text="Le PAF player")

        self.onglets.grid(row=0, column=0, sticky="nw")

        
# on utilise le timer fait sur mesure. je ne sais pas trop pourquoi :)
        self.timer = ttkTimer(self.OnTimer, 1.0)
        self.timer.start()

# on lance VLC
        self.vlci = vlc.Instance()
        self.vlcplayer = self.vlci.media_player_new()


# Ici on met en plance les elements du player

        # listbox contient la liste des morceaux du genre selectionne
        self.listbox = tkinter.Listbox(self.player,selectmode=tkinter.SINGLE,width = 100,height = 30,background=self.player.cget('bg'),relief=tkinter.FLAT,bd=0)
        self.listbox.bind('<Double-Button>', self.OnListEnter)
        self.listbox.bind("<Return>", self.OnListEnter)
        self.listbox.grid(column=0, row=0, columnspan=6)
        
        # les quatre boutons de controle
        self.pause  = ttk.Button(self.player, text="Pause", command=self.OnPause)
        self.play   = ttk.Button(self.player, text="Play", command=self.OnPlay)
        self.stop   = ttk.Button(self.player, text="Stop", command=self.OnStop)
        self.back   = ttk.Button(self.player, text="Back", command=self.OnBack)
        
        self.pause.grid(column=0, row=1)
        self.play.grid(column=1, row=1)
        self.stop.grid(column=2, row=1)
        self.back.grid(column=3, row=1)
        

        # le volume
        self.volume_var = tkinter.IntVar()
        self.volslider = tkinter.Scale(self.player, variable=self.volume_var, command=self.volume_sel,
                from_=0, to=100, orient=tkinter.HORIZONTAL, length=300)
        self.volslider.grid(column=4, row=1)
        

        # le time slider        
        self.scale_var = tkinter.DoubleVar()
        self.timeslider_last_val = ""
        self.timeslider = tkinter.Scale(self.player, variable=self.scale_var, command=self.scale_sel,
                from_=0, to=1000, orient=tkinter.HORIZONTAL, length=800)
        self.timeslider.grid(column=0, row=2, columnspan=5)
        self.timeslider_last_update = time.time()
        
        self.boardactive = True

        
    def CloseBoard(self):
        self.boardactive = False
        if not(self.vlcplayer is None):
            self.vlcplayer.stop()
        self.swindow.destroy()
        


# les deux fonctions suivantes sont pour la selection du repertoire


    def OnFileButtonClick(self):
        self.dirpath = filedialog.askdirectory(title="Selectionner le répertoire de musique",initialdir="~/Bureau")
        self.chemin.set(self.dirpath)
        if self.dirpath:
            self.genbutton['state']='normal'

    def OnPressEnter(self,event):
        self.dirpath = filedialog.askdirectory(title="Selectionner le répertoire de musique")
        self.chemin.set(self.dirpath)
        
# cette fonction genere le pafboard
    
    def OnGenButtonClick(self):
        self.contenu = self.bb(self.dirpath).contenu
        k=0
        self.clefs=list(self.contenu.keys())
        self.clefs.sort()
        if not(self.boardactive):
            self.CreateBoard()
        for k in range(len(self.clefs)):
            button = tkinter.Button(self.board, font=('Latin Modern Roman', -self.buttonpolicesize, 'bold'),height=2, width=15, foreground='white', wraplength=self.buttonpolicesize*8, bg = 'blue', text=self.clefs[k] + " (" + str(len(self.contenu[self.clefs[k]])) + ")", command=lambda x=self.clefs[k]: self.UpdatePlayer(x))
            button.grid(row=int(k/self.nb_cols),column=k%self.nb_cols)
        

    def UpdatePlayer(self,l):
        """Met a jour la liste de morceaux dans le player
        """
        # au cas ou le player a ete ferme
        if not(self.boardactive):
            self.CreateBoard()

        # ce sont les chansons du genre en question
        self.seltracks = self.contenu[l]
        self.seltracks.sort()
        self.listbox.delete(0, tkinter.END)
        for i in self.seltracks:
            self.listbox.insert(tkinter.END, i.track + " (" + i.genre + ")")
        self.player.update()
        self.onglets.select(self.player)
        
# pour finir, toutes les fonctions du player

    def OnListEnter(self, evt):
        p=self.listbox.curselection()
        trackfile = self.seltracks[p[0]]
        self.Media = self.vlci.media_new(trackfile.chemin)
        self.vlcplayer.set_media(self.Media)
        self.OnPlay()
        self.volslider.set(80)


    def OnPlay(self):
        """Toggle the status to Play/Pause.
        If no file is loaded, open the dialog window.
        """
        if self.Media == None and self.seltracks != None:
            trackfile = self.seltracks[0]
            self.Media = self.vlci.media_new(trackfile.chemin)
            self.vlcplayer.set_media(self.Media)
        elif self.Media == None and self.seltracks == None:
            self.errorDialog("Impossible de jouer.\nCharger un morceau!")
            return
        if self.vlcplayer.play() == -1:
            self.errorDialog("Impossible de jouer.")


    def OnPause(self):
        """Pause the player.
        """
        self.vlcplayer.pause()


    def OnBack(self):
        """Pause the player.
        """
        self.onglets.select(self.board)

        

    def OnStop(self):
        """Stop the player.
        """
        self.vlcplayer.stop()
        # reset the time slider
        self.timeslider.set(0)
    
    def OnTimer(self):
        """Update the time slider according to the current movie time.
        """
        if self.vlcplayer == None or not(self.boardactive):
            return
        # since the self.player.get_length can change while playing,
        # re-set the timeslider to the correct range.
        length = self.vlcplayer.get_length()
        dbl = length * 0.001
        self.timeslider.config(to=dbl)

        # update the time on the slider
        tyme = self.vlcplayer.get_time()
        if tyme == -1:
            tyme = 0
        dbl = tyme * 0.001
        self.timeslider_last_val = ("%.0f" % dbl) + ".0"
        # don't want to programatically change slider while user is messing with it.
        # wait 2 seconds after user lets go of slider
        if time.time() > (self.timeslider_last_update + 2.0):
            self.timeslider.set(dbl)

            
    def scale_sel(self, evt):
        if self.player == None:
            return
        nval = self.scale_var.get()
        sval = str(nval)
        if self.timeslider_last_val != sval:
            # this is a hack. The timer updates the time slider.
            # This change causes this rtn (the 'slider has changed' rtn) to be invoked.
            # I can't tell the difference between when the user has manually moved the slider and when
            # the timer changed the slider. But when the user moves the slider tkinter only notifies
            # this rtn about once per second and when the slider has quit moving.
            # Also, the tkinter notification value has no fractional seconds.
            # The timer update rtn saves off the last update value (rounded to integer seconds) in timeslider_last_val
            # if the notification time (sval) is the same as the last saved time timeslider_last_val then
            # we know that this notification is due to the timer changing the slider.
            # otherwise the notification is due to the user changing the slider.
            # if the user is changing the slider then I have the timer routine wait for at least
            # 2 seconds before it starts updating the slider again (so the timer doesn't start fighting with the
            # user)
            self.timeslider_last_update = time.time()
            mval = "%.0f" % (nval * 1000)
            self.vlcplayer.set_time(int(mval)) # expects milliseconds


    def volume_sel(self, evt):
        if self.vlcplayer == None:
            return
        volume = self.volume_var.get()
        if volume > 100:
            volume = 100
        if self.vlcplayer.audio_set_volume(volume) == -1:
            self.errorDialog("Mis à jour du volume impossible.")

    def OnToggleVolume(self, evt):
        """Mute/Unmute according to the audio button.
        """
        is_mute = self.vlcplayer.audio_get_mute()

        self.vlcplayer.audio_set_mute(not is_mute)
        # update the volume slider;
        # since vlc volume range is in [0, 200],
        # and our volume slider has range [0, 100], just divide by 2.
        self.volume_var.set(self.vlcplayer.audio_get_volume())

    def OnSetVolume(self):
        """Set the volume according to the volume sider.
        """
        volume = self.volume_var.get()
        # vlc.MediaPlayer.audio_set_volume returns 0 if success, -1 otherwise
        if volume > 100:
            volume = 100
        if self.vlcplayer.audio_set_volume(volume) == -1:
            self.errorDialog("Mis à jour du volume impossible.")

    def errorDialog(self, errormessage):
        """Display a simple error dialog.
        """
        tkinter.messagebox.showerror(self, errormessage)

def _quit():
    print("_quit: bye")
    app.quit()     # stops mainloop
    app.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate
    os._exit(1)

    
if __name__ == "__main__":
    app = paf_board(None)
    app.title('Créer un PAF board')
    app.protocol("WM_DELETE_WINDOW", _quit)
    app.mainloop()
