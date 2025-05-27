# 📬 InboxGuard - Action Service

**Actions-Service** est l’un des modules principaux du projet **InboxGuard**, un système distribué de détection et de réaction automatique au phishing par email.

Ce module est responsable de l'exécution des **actions système automatisées** sur les emails d'une boîte de réception en fonction d’un **score de phishing** fourni par un modèle d'IA.

---

## 🚀 Fonctionnalité principale

Le module permet de :

- Se connecter à une boîte email via **IMAP**
- Lire les emails et leurs scores (transmis en interne)
- Appliquer automatiquement une action :
  - ✅ Ne rien faire (score faible)
  - 🏷️ Marquer comme suspect
  - ⚠️ Déplacer dans un dossier "Suspect"
  - ❌ Déplacer dans "Spam" ou supprimer

---

## 🛠️ Technologies utilisées

- **Bash** : script principal (`inboxguard_actions.sh`)
- **Python 3 (imaplib)** : gestion des actions IMAP (`imap_action.py`)
- **Gmail IMAP** pour les tests réels
- Simulation de scores IA côté Bash

---

## 📁 Structure du projet

action-service/

├── inboxguard_actions.sh # Script Bash principal

├── imap_action.py # Script Python pour les actions IMAP

├── emails/ # Dossier de tests locaux

├── quarantine/ # Dossier local simulant la quarantaine

├── logs/ # Fichier de log des actions


---

## ⚙️ Pré-requis

### 📌 Côté système
- Linux, WSL ou environnement Bash compatible
- Python 3 installé (`python3 --version`)
- Git installé

### 📌 Côté Gmail
Pour pouvoir exécuter des actions réelles sur ta boîte Gmail via IMAP :

#### 1. **Activer l’authentification à deux facteurs (2FA)**

👉 [https://myaccount.google.com/security](https://myaccount.google.com/security)

#### 2. **Générer un mot de passe d’application**

👉 [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)

- Choisir : "Autre (nom personnalisé)" → `InboxGuard`
- Copier le mot de passe généré (ex: `abcd efgh ijkl mnop`)
- L’utiliser à la place de ton mot de passe Gmail dans le script

#### 3. **Activer IMAP dans Gmail**

👉 [https://mail.google.com/mail/u/0/#settings/fwdandpop](https://mail.google.com/mail/u/0/#settings/fwdandpop)

- Cocher “Activer le protocole IMAP”
- Enregistrer les modifications

---

## 🧪 Exemple d'utilisation

### 🔸 Commande de base :
```bash
./inboxguard_actions.sh -u youremail@gmail.com -p "mot_de_passe_app" -s imap.gmail.com -m

Usage: ./inboxguard_actions.sh -u <email> -p <password> -s <imap_server> -m [-l logfile] [--restore]
Options:
  -u <email>       : Adresse email
  -p <password>    : Mot de passe d'application (Gmail)
  -s <imap_server> : Serveur IMAP (ex: imap.gmail.com)
  -m               : Active les actions automatiques
  -l <logfile>     : Spécifie un fichier de log personnalisé
  --restore        : Restaure les emails depuis la quarantaine (root uniquement)
  -h               : Affiche cette aide

Exemple de log généré
2025-05-15-23-50-00 : ayoub17 : INFOS : Action tag appliquée sur email 002 (score=67)
2025-05-15-23-50-01 : ayoub17 : INFOS : Action quarantine appliquée sur email 003 (score=92)

