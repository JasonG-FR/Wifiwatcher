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

def main(args):
    #Pour rappel, le script est lancé avec les droits root !
    #On vérifie si la carte Wifi est reconnue
    
    interface = "wlan0"

    try:
        subprocess.check_output(["ifconfig " + interface], shell=True)
        print(interface + "connectée !")
        interface_OK = True
    except subprocess.CalledProcessError:
        print(interface + " non connectée !")
        interface_OK = False
    
    if interface_OK:
        #Vérifier que le package existe
        
            #Vérifier qu'il est à jour
    else:
        #Installer le package disponible
        #Redémarrer système
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
