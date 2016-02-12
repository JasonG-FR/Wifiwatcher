#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Wifiwatcher.py
#  
#  Copyright 2016 Jason Gombert <jason.gombert@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

import subprocess

def installPkg(nomPkg):
    subprocess.check_output(["pacman -U " + nomPkg], shell=True)

def buildPkg():
    subprocess.check_output(["sudo -u oracle yaourt -G 8188eu-dkms"], shell=True)
    subprocess.check_output(["cd 8188eu-dkms"], shell=True)
    subprocess.check_output(["sudo -u oracle makepkg -c"], shell=True)
    subprocess.check_output(["cd .."], shell=True)
    
    return subprocess.check_output(["ls *.pkg.tar.xz"], shell=True)

def main(args):
    #Pour rappel, le script est lancé avec les droits root !
    #On vérifie si la carte Wifi est reconnue
    
    #interface = "wlan0"
    interface = "wlp3s0"

    try:
        subprocess.check_output(["ifconfig " + interface], shell=True)
        print(interface + " connectée !")
        interface_OK = True
    except subprocess.CalledProcessError:
        print(interface + " non connectée !")
        interface_OK = False
    
    if interface_OK:
        #Vérifier que le package existe
        try:
            subprocess.check_output(["ls 8188eu-dkms/"], shell=True)
            existe = True
        except subprocess.CalledProcessError:
            existe = False
            
        if existe:
            print(res)
            #Vérifier qu'il est à jour
            
        #Sinon on télécharge et compile le dernier
        else:
            #Compilation du package
            nom = buildPkg()
            #Installation du package
            installPkg(nom)
    else:
        print("er")
        #Installer le package disponible
        #Redémarrer système
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
