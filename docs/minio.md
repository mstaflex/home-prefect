# MinIO Cheat Sheet (`mc` CLI)

> `mc` = MinIO Client. `local` ist der Alias für die eigene MinIO-Instanz.

---

## Verbindung / Alias

```bash
# Alias einrichten (einmalig)
mc alias set local http://localhost:9000 ACCESSKEY SECRETKEY

# Verbindung testen
mc admin info local
```

---

## Buckets

```bash
# Alle Buckets auflisten
mc ls local

# Bucket erstellen
mc mb local/mein-bucket

# Bucket löschen (nur wenn leer)
mc rb local/mein-bucket

# Bucket löschen mit allem Inhalt (Vorsicht!)
mc rb --force local/mein-bucket
```

---

## Dateien / Objekte

```bash
# Inhalt eines Buckets anzeigen
mc ls local/mein-bucket

# Datei hochladen
mc cp ./datei.txt local/mein-bucket/

# Datei herunterladen
mc cp local/mein-bucket/datei.txt ./

# Ordner rekursiv hochladen
mc cp --recursive ./ordner/ local/mein-bucket/ordner/

# Datei löschen
mc rm local/mein-bucket/datei.txt

# Alle Dateien in einem Bucket löschen (Vorsicht!)
mc rm --recursive --force local/mein-bucket
```

---

## Benutzer verwalten

```bash
# Alle Benutzer auflisten
mc admin user list local

# Benutzer erstellen
mc admin user add local BENUTZERNAME PASSWORT

# Benutzer deaktivieren
mc admin user disable local BENUTZERNAME

# Benutzer löschen
mc admin user remove local BENUTZERNAME

# Benutzerdetails anzeigen (inkl. zugewiesener Policies)
mc admin user info local BENUTZERNAME
```

---

## Policies (Zugriffsrechte)

```bash
# Alle Policies auflisten
mc admin policy list local

# Policy anzeigen
mc admin policy info local POLICYNAME

# Policy aus JSON-Datei erstellen
mc admin policy create local POLICYNAME policy.json

# Policy einem Benutzer zuweisen
mc admin policy attach local POLICYNAME --user BENUTZERNAME

# Policy von einem Benutzer entfernen
mc admin policy detach local POLICYNAME --user BENUTZERNAME

# Policy löschen
mc admin policy remove local POLICYNAME
```

### Beispiel: Policy-Datei (nur lesen & schreiben, kein Löschen)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:ListBucket", "s3:GetBucketLocation"],
      "Resource": ["arn:aws:s3:::mein-bucket"]
    },
    {
      "Effect": "Allow",
      "Action": ["s3:PutObject", "s3:GetObject"],
      "Resource": ["arn:aws:s3:::mein-bucket/*"]
    },
    {
      "Effect": "Deny",
      "Action": ["s3:DeleteObject"],
      "Resource": ["arn:aws:s3:::mein-bucket/*"]
    }
  ]
}
```

---

## Bucket-Zugriffsrechte (öffentlich / privat)

```bash
# Bucket öffentlich lesbar machen
mc anonymous set download local/mein-bucket

# Bucket komplett öffentlich machen (lesen + schreiben)
mc anonymous set public local/mein-bucket

# Bucket wieder privat setzen
mc anonymous set none local/mein-bucket

# Aktuellen Status anzeigen
mc anonymous get local/mein-bucket
```

---

## Nützliches

```bash
# Speichernutzung eines Buckets anzeigen
mc du local/mein-bucket

# Ereignisse / Logs anzeigen
mc admin logs local

# MinIO-Server-Status
mc admin info local

# Spiegelung: lokalen Ordner mit Bucket synchronisieren
mc mirror ./lokaler-ordner/ local/mein-bucket/
```
