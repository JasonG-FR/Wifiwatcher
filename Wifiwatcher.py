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

def mettreAJour(user,nomPkg,log,repoAUR):
    subprocess.run(["sudo -u " + user + " mkdir tmp"], shell=True)
    subprocess.run(["cd tmp && sudo -u " + user + " git clone " + repoAUR], shell=True)
    
    PKGBUILD_local = open(nomPkg + "/PKGBUILD","r")
    PKGBUILD_internet = open("tmp/" + nomPkg + "/PKGBUILD","r")
    
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
    
    log.write("Version de " + nomPkg + " : [dépôt] " + versionInternet.replace("pkgver=","").replace("\n","") + " | [local] " + versionLocale.replace("pkgver=","").replace("\n","") + "\n")
    log.flush()
    if versionInternet == versionLocale:
        log.write("Le package local est à jour!\n")
        log.flush()
        return False
    else:
        log.write("Le package local doit être mis à jour!\n")
        log.flush()
        return True

def installPkg(nomPkg):
    subprocess.check_output(["pacman -U --noconfirm " + nomPkg], shell=True)

def buildPkg(user,nomPkg,repoAUR):
    subprocess.run(["sudo -u " + user + " git clone " + repoAUR], shell=True)
    subprocess.run(["cd " + nomPkg + " && sudo -u " + user + " makepkg -c"], shell=True)
    
    return subprocess.check_output(["ls " + nomPkg + "/*.pkg.tar.xz"], shell=True).decode("utf8")

def pkgExiste(nomPkg):
    try:
        subprocess.check_output(["ls " + nomPkg + "/*.pkg.tar.xz"], shell=True)
        return True
    except subprocess.CalledProcessError:
        return False


def main(args):
    #Pour rappel, le script est lancé avec les droits root !
    
    interface = "wlan0"
    interface_secours = "eth0"
    user = "oracle"
    nomPkg = "8188eu-dkms"
    repoAUR = "https://aur.archlinux.org/8188eu-dkms.git"
    
    log = open("logs/Wifiwatcher.log","a")
    
    log.write("\n\t---- Wifiwatcher ----\n")
    log.flush()
    #On affiche la date (logs)
    date = subprocess.check_output(["date"], shell=True).decode("utf8")
    log.write(date)
    log.flush()
    
    #On vérifie qu'on est root
    
    whoami = subprocess.check_output(["whoami"], shell=True)
    if whoami != b'root\n':
        log.write("Wifiwatcher a besoin d'être lancé en tant que root ! (lancé avec "+ whoami.decode("utf8") +")\n")
        log.flush()
        return 1
    
    #On vérifie si la carte Wifi est reconnue
    try:
        subprocess.check_output(["ifconfig " + interface], shell=True)
        log.write(interface + " connectée !\n")
        log.flush()
        interface_OK = True
    except subprocess.CalledProcessError:
        log.write(interface + " non connectée !\n")
        log.flush()
        interface_OK = False
    
    if interface_OK:
        #Vérifier que le package existe (*.pkg.tar.xz)
        if pkgExiste(nomPkg):
            log.write("Il existe un package local, est-il à jour ?\n")
            log.flush()
            #Vérifier qu'il est à jour
            if mettreAJour(user,nomPkg,log,repoAUR):
                #On sauvegarde l'ancien package (on sait jamais...)
                log.write("Sauvegarde ancien package\n")
                log.flush()
                subprocess.check_output(["mv " + nomPkg + "/ " + nomPkg + "-old/"], shell=True)
                #Téléchargement et compilation du package
                log.write("Téléchargement et compilation du package\n")
                log.flush()
                nom = buildPkg(user,nomPkg,repoAUR)
                #Installation du package
                log.write("Installation du package\n")
                log.flush()
                installPkg(nom)
                            
        #Sinon on télécharge et compile le dernier
        else:
            #Téléchargement et compilation du package
            log.write("Téléchargement et compilation du package\n")
            log.flush()
            nom = buildPkg(user,nomPkg,repoAUR)
            #Installation du package
            log.write("Installation du package\n")
            log.flush()
            installPkg(nom)

    else:
        if pkgExiste(nomPkg):
            #Installer le package disponible
            log.write("Installation du package\n")
            log.flush()
            nom = subprocess.check_output(["ls " + nomPkg + "/*.pkg.tar.xz"], shell=True).decode("utf8")
            installPkg(nom)
            
        else:
            log.write("La carte Wifi est désactivée et aucun package de " + nomPkg + " disponible localement...\n")
            log.flush()
            #Pas de Wifi ni de package disponible, on peut rien faire... sauf si on a un accès Ethernet !
            #Attente d'une connection Ethernet...
            log.write("Attente d'une connection Ethernet...\n")
            log.flush()
            nonConnecte = True
            while nonConnecte:
                if_sec = subprocess.check_output(["ifconfig " + interface_secours], shell=True).decode("utf8")
                #Si interface_secours a une IP, alors on est connecté
                if "inet" in if_sec:
                    nonConnecte = False
                time.sleep(5)
            log.write(interface_secours + " connectée !\n")
            log.flush()
            #Téléchargement et compilation du package
            log.write("Téléchargement et compilation du package\n")
            log.flush()
            nom = buildPkg(user,nomPkg,repoAUR)
            #Installation du package
            log.write("Installation du package\n")
            log.flush()
            installPkg(nom)
            
        #Redémarrer système dans 1 minute (pour pouvoir quitter le script et sauvegarder les logs!)
        subprocess.run(["shutdown -r +1 'Redémarrage système imminent pour réactivation du Wifi...'"], shell=True)
        log.write("---- Reboot ----\n")
        log.flush()
        log.close()
            
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
