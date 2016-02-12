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
import time

def mettreAJour(user):
    subprocess.run(["sudo -u " + user + " mkdir tmp"], shell=True)
    subprocess.run(["cd tmp && sudo -u " + user + " yaourt -G 8188eu-dkms"], shell=True)
    
    PKGBUILD_local = open("8188eu-dkms/PKGBUILD","r")
    PKGBUILD_internet = open("tmp/8188eu-dkms/PKGBUILD","r")
    
    data_local = PKGBUILD_local.readlines()
    data_internet = PKGBUILD_internet.readlines()
    
    for ligne in data_local:
        if "pkgver=" in ligne:
            versionLocale = ligne
    for ligne in data_internet:
        if "pkgver=" in ligne:
            versionInternet = ligne
    
    PKGBUILD_local.close()
    PKGBUILD_internet.close()
    subprocess.check_output(["rm -r tmp"], shell=True)
    
    print("Version de 8188eu-dkms : [dépôt] " + versionInternet.replace("pkgver=","").replace("\n","") + " | [local] " + versionLocale.replace("pkgver=","").replace("\n",""))
    if versionInternet == versionLocale:
        print("Le package local est à jour!")
        return False
    else:
        print("Le package local doit être mis à jour!")
        return True

def installPkg(nomPkg):
    subprocess.check_output(["pacman -U --noconfirm" + nomPkg], shell=True)

def buildPkg(user):
    subprocess.run(["sudo -u " + user + " yaourt -G 8188eu-dkms"], shell=True)
    subprocess.run(["cd 8188eu-dkms && sudo -u " + user + " makepkg -c"], shell=True)
    
    return subprocess.check_output(["ls 8188eu-dkms/*.pkg.tar.xz"], shell=True).decode("utf8")

def pkgExiste():
    try:
        subprocess.check_output(["ls 8188eu-dkms/*.pkg.tar.xz"], shell=True)
        return True
    except subprocess.CalledProcessError:
        return False


def main(args):
    #Pour rappel, le script est lancé avec les droits root !
    
    interface = "wlan0"
    user = "oracle"
    
    print("\n\t---- Wifiwatcher ----")
    #On affiche la date (logs)
    subprocess.run(["date"], shell=True)
    
    #On vérifie qu'on est root
    
    whoami = subprocess.check_output(["whoami"], shell=True)
    if whoami != b'root\n':
        print("Wifiwatcher a besoin d'être lancé en tant que root ! (lancé avec "+ whoami.decode("utf8") +")")
        return 1
    
    #On vérifie si la carte Wifi est reconnue
    try:
        subprocess.check_output(["ifconfig " + interface], shell=True)
        print(interface + " connectée !")
        interface_OK = True
    except subprocess.CalledProcessError:
        print(interface + " non connectée !")
        interface_OK = False
    
    if interface_OK:
        #Vérifier que le package existe (*.pkg.tar.xz)
        if pkgExiste():
            print("Il existe un package local, est-il à jour ?")
            #Vérifier qu'il est à jour
            if mettreAJour(user):
                #On sauvegarde l'ancien package (on sait jamais...)
                subprocess.check_output(["mv 8188eu-dkms/ 8188eu-dkms-old/"], shell=True)
                #Téléchargement et compilation du package
                nom = buildPkg(user)
                #Installation du package
                installPkg(nom)
                            
        #Sinon on télécharge et compile le dernier
        else:
            #Téléchargement et compilation du package
            nom = buildPkg(user)
            #Installation du package
            installPkg(nom)

    else:
        if pkgExiste():
            #Installer le package disponible
            nom = subprocess.check_output(["ls 8188eu-dkms/*.pkg.tar.xz"], shell=True).decode("utf8")
            installPkg(nom)
            
        else:
            print("La carte Wifi est désactivée et aucun package de 8188eu-dkms disponible localement...")
            #Pas de Wifi ni de package disponible, on peut rien faire... sauf si on a un accès Ethernet !
            #Attente d'une connection Ethernet...
            print("Attente d'une connection Ethernet...")
            nonConnecte = True
            while nonConnecte:
                eth0 = subprocess.check_output(["ifconfig eth0"], shell=True).decode("utf8")
                #Si eth0 à une IP, alors on est connecté
                if "inet" in eth0:
                    nonConnecte = False
                time.sleep(5)
            print("eth0 connectée !")
            #Téléchargement et compilation du package
            nom = buildPkg(user)
            #Installation du package
            installPkg(nom)
            
        #Redémarrer système dans 1 minute (pour pouvoir quitter le script et sauvegarder les logs!)
        subprocess.run(["shutdown -r +1 'Redémarrage système imminent pour réactivation du Wifi...'"], shell=True)
        print("---- Reboot ----")
            
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
