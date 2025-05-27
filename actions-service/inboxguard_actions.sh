#!/bin/bash

# ============================
# InboxGuard - Email Actions
# ============================

# ========== CONFIG ==========
EMAIL=""
PASSWORD=""
SERVER=""
ACTION_MODE=false
LOG_FILE="./logs/history.log"
EMAIL_ID=""
QUARANTINE_DIR="./quarantine"
SIMULATE=false
RESTORE_MODE=false

# ========== USAGE ==========
usage() {
  echo "Usage: $0 -u <email> -p <password> -s <imap_server> -m [-l logfile] [--restore]"
  echo "Options:"
  echo "  -u <email>       : Adresse email"
  echo "  -p <password>    : Mot de passe"
  echo "  -s <imap_server> : Serveur IMAP (ex: imap.gmail.com)"
  echo "  -m               : Active les actions automatiques"
  echo "  -l <logfile>     : Spécifie un fichier de log personnalisé"
  echo "  --restore        : Restaure les emails depuis la quarantaine (admin uniquement)"
  echo "  -h               : Affiche cette aide"
  exit 1
}

# ========== LOGGING ==========
log_action() {
  local type="$1"
  local message="$2"
  local now=$(date '+%Y-%m-%d-%H-%M-%S')
  echo "$now : $(whoami) : $type : $message" | tee -a "$LOG_FILE"
}

# ========== RESTORE ==========
restore_emails() {
  if [ "$(whoami)" != "root" ]; then
    log_action "ERROR" "Permission refusée pour --restore"
    exit 102
  fi
  mkdir -p ./emails
  for f in "$QUARANTINE_DIR"/*; do
    mv "$f" ./emails/
    log_action "INFOS" "Email restauré depuis quarantaine : $(basename "$f")"
  done
  exit 0
}

# ========== ACTION ==========
perform_action() {
  local email_id="$1"
  local score="$2"
  local action="safe"

  if [ "$score" -le 30 ]; then
    action="safe"
  elif [ "$score" -le 60 ]; then
    action="flag"
  elif [ "$score" -le 85 ]; then
    action="tag"
  else
    action="quarantine"
  fi

  # Appel du script Python pour exécuter l'action réelle via IMAP
  if python3 imap_action.py \
    --email "$EMAIL" \
    --pass "$PASSWORD" \
    --server "$SERVER" \
    --mailid "$email_id" \
    --action "$action"
  then
    log_action "INFOS" "Action $action appliquée sur email $email_id (score=$score)"
  else
    log_action "ERROR" "Échec de l'action $action sur email $email_id"
  fi
}

# ========== PARAMÈTRES ==========
while [[ "$#" -gt 0 ]]; do
  case "$1" in
    -u) EMAIL="$2"; shift ;;
    -p) PASSWORD="$2"; shift ;;
    -s) SERVER="$2"; shift ;;
    -m) ACTION_MODE=true ;;
    -l) LOG_FILE="$2"; shift ;;
    --restore) RESTORE_MODE=true ;;
    -h) usage ;;
    *) echo "Option inconnue: $1"; usage ;;
  esac
  shift
done

# ========== VALIDATION ==========
if $RESTORE_MODE; then
  restore_emails
fi

if [ -z "$EMAIL" ] || [ -z "$PASSWORD" ] || [ -z "$SERVER" ]; then
  log_action "ERROR" "Paramètres de connexion manquants"
  exit 101
fi

# Simuler récupération d'emails et scores depuis IA
# Ici on simule 3 emails avec des scores (ceci sera intégré plus tard avec le module IA)
declare -A EMAIL_SCORES
EMAIL_SCORES=( ["001"]=25 ["002"]=67 ["003"]=92 )

log_action "INFOS" "Connexion simulée à $SERVER en tant que $EMAIL"

# Traitement des emails en parallèle (fork simulation)
for email_id in "${!EMAIL_SCORES[@]}"; do
  score="${EMAIL_SCORES[$email_id]}"
  (
    perform_action "$email_id" "$score"
  ) &
done
wait

log_action "INFOS" "Traitement terminé."

exit 0
