# 📘 **Document de Diagrammes de Séquence – Application de Gestion de Logement**

## 🧭 **1. Vue Générale**

Chaque diagramme de séquence présente un scénario utilisateur (cas d’utilisation) avec les messages échangés entre les objets du système (ex. : contrôleurs, classes métiers, services externes).

---

## 🧾 **2. Scénarios Détaillés**

---

### 📍 **UC1 – Création de compte (Client)**

```plaintext
Client → Frontend : Saisie téléphone/email
Frontend → AuthService : Demander OTP
AuthService → SMSService : Envoyer OTP

Client → Frontend : Saisie OTP
Frontend → AuthService : Vérifier OTP
AuthService → Utilisateur : Créer Client
AuthService → DB : Enregistrer Client
AuthService → Frontend : Succès
```

---

### 📍 **UC2 – Recherche de logement**

```plaintext
Client → Frontend : Entrer critères (lieu, prix, type)
Frontend → LogementController : GET /logements
LogementController → LogementService : Rechercher
LogementService → DB : Filtrer logements
DB → LogementService : Liste<Logement>
LogementService → LogementController : Résultats
LogementController → Frontend : Liste logements
Frontend → Client : Afficher résultats
```

---

### 📍 **UC3 – Réservation d’un logement**

```plaintext
Client → Frontend : Cliquer "Réserver"
Frontend → RéservationController : POST /réservations
RéservationController → LogementService : Vérifier disponibilité
LogementService → DB : Check disponibilités

RéservationController → RéservationService : Créer réservation
RéservationService → DB : Sauvegarder Réservation
RéservationService → PaiementService : Initialiser paiement
PaiementService → MobileMoneyAPI : Débit acompte

MobileMoneyAPI → PaiementService : Confirmation
PaiementService → DB : Marquer paiement "réussi"
RéservationController → Frontend : Confirmation réservation
```

---

### 📍 **UC4 – Messagerie client ↔ agent**

```plaintext
Client → Frontend : Saisir message
Frontend → MessageController : POST /messages
MessageController → DB : Enregistrer message
MessageController → PushService : Notifier agent

Agent → Frontend : Consulter message
Frontend → MessageController : GET /messages?logement=ID
MessageController → DB : Charger historique
MessageController → Frontend : Liste<Message>
```

---

### 📍 **UC5 – Ajout d’un logement (Agent)**

```plaintext
Agent → Frontend : Remplit formulaire ajout logement
Frontend → LogementController : POST /logements
LogementController → LogementService : Créer logement
LogementService → DB : Sauvegarder logement
LogementService → FichierService : Upload photos
FichierService → Storage : Stocker fichiers
LogementService → DB : Associer fichiers au logement
LogementController → Frontend : Succès publication
```

---

### 📍 **UC6 – Commentaire après séjour**

```plaintext
Client → Frontend : Noter logement
Frontend → CommentaireController : POST /commentaires
CommentaireController → DB : Sauvegarder commentaire
CommentaireController → AdminReviewQueue : Ajouter pour modération
CommentaireController → Frontend : Message "commentaire soumis"
```

---

### 📍 **UC7 – Validation de compte agent (Admin)**

```plaintext
Admin → BackOffice : Voir demandes de vérification
BackOffice → UtilisateurService : GET /utilisateurs?type=Agent&statut=EnAttente
UtilisateurService → DB : Récupérer agents
Admin → BackOffice : Valider agent

BackOffice → UtilisateurService : PUT /utilisateurs/:id
UtilisateurService → DB : Mettre statut = Validé
UtilisateurService → EmailService : Envoyer notification agent
```
