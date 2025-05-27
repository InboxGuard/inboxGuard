# imap_action.py
# Script Python appelé depuis Bash pour réaliser des actions réelles sur une boîte mail via IMAP

import imaplib
import argparse
import sys

# ========== Parser des arguments ==========
parser = argparse.ArgumentParser(description="InboxGuard - IMAP Action Handler")
parser.add_argument('--email', required=True, help='Adresse email (login)')
parser.add_argument('--pass', required=True, dest='password', help='Mot de passe')
parser.add_argument('--server', required=True, help='Serveur IMAP')
parser.add_argument('--mailid', required=True, help='Identifiant du mail (index simplifié)')
parser.add_argument('--action', required=True, choices=['safe', 'flag', 'tag', 'delete', 'quarantine'], help='Action à appliquer')
args = parser.parse_args()

try:
    # Connexion au serveur
    mail = imaplib.IMAP4_SSL(args.server)
    mail.login(args.email, args.password)
    mail.select("inbox")  # ou autre dossier

    # Recherche des emails
    typ, data = mail.search(None, 'ALL')
    ids = data[0].split()

    if not ids:
        print("ERROR: Aucun email trouvé.")
        sys.exit(103)

    # Choisir l'email ciblé
    if args.mailid.isdigit() and int(args.mailid) < len(ids):
        mail_id = ids[int(args.mailid)]
    else:
        mail_id = ids[-1]  # dernier email si index invalide

    # Appliquer l'action
    if args.action == "safe":
        print(f"[SAFE] Aucun changement pour l'email {mail_id.decode()}")

    elif args.action == "flag":
        mail.store(mail_id, '+FLAGS', '\\Flagged')
        print(f"[FLAG] Email {mail_id.decode()} marqué comme important.")

    elif args.action == "tag":
        mail.create("Suspect")  # Crée le dossier si pas encore existant
        mail.copy(mail_id, "Suspect")
        print(f"[TAG] Email {mail_id.decode()} déplacé dans 'Suspect'.")

    elif args.action == "quarantine":
        mail.copy(mail_id, "[Gmail]/Spam")
        mail.store(mail_id, '+FLAGS', '\\Deleted')
        print(f"[QUARANTINE] Email {mail_id.decode()} déplacé dans Spam.")

    elif args.action == "delete":
        mail.store(mail_id, '+FLAGS', '\\Deleted')
        mail.expunge()
        print(f"[DELETE] Email {mail_id.decode()} supprimé.")

    mail.logout()

except Exception as e:
    print(f"ERROR: {str(e)}")
    sys.exit(104)
