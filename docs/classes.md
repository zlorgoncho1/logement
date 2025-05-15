# 📐 **Document de Diagramme de Classes – Plateforme de Gestion de Logement (Sénégal)**

## 🧱 **1. Vue d’Ensemble**

Ce diagramme de classes reflète les entités centrales de l’application : utilisateurs (clients, agents), logements, réservations, paiements, messagerie, commentaires, et les opérations d’administration.

---

## 🧩 **2. Classes Principales**

### 🔹 `Utilisateur`

Représente un compte générique dans le système (Client ou Agent Immobilier).

```plaintext
+ id : UUID
+ nom : string
+ prénom : string
+ email : string
+ téléphone : string
+ type : enum {Client, Agent}
+ motDePasse : string
+ dateCréation : datetime
```

### 🔹 `Client` (hérite de `Utilisateur`)

Classe spécifique aux clients.

```plaintext
+ favoris : List<Logement>
```

### 🔹 `AgentImmobilier` (hérite de `Utilisateur`)

Classe spécifique aux agents.

```plaintext
+ documentsKYC : List<Fichier>
+ logements : List<Logement>
```

---

### 🔹 `Logement`

```plaintext
+ id : UUID
+ titre : string
+ type : enum {Maison, Appartement, Studio, Chambre}
+ adresse : string
+ description : text
+ prixParNuit : decimal
+ équipements : List<string>
+ photos : List<Fichier>
+ statut : enum {Publié, Désactivé, EnAttente}
+ agent : AgentImmobilier
+ disponibilités : List<Disponibilité>
```

### 🔹 `Disponibilité`

```plaintext
+ id : UUID
+ logement : Logement
+ dateDébut : date
+ dateFin : date
+ estDisponible : bool
```

---

### 🔹 `Réservation`

```plaintext
+ id : UUID
+ client : Client
+ logement : Logement
+ dateDébut : date
+ dateFin : date
+ statut : enum {EnAttente, Confirmée, Annulée, Terminée}
+ montantTotal : decimal
+ acompte : decimal
+ dateCréation : datetime
+ paiement : Paiement
```

### 🔹 `Paiement`

```plaintext
+ id : UUID
+ réservation : Réservation
+ méthode : enum {MobileMoney, Carte, Espèces}
+ statut : enum {EnAttente, Réussi, Échoué, Remboursé}
+ montant : decimal
+ datePaiement : datetime
```

---

### 🔹 `Message`

```plaintext
+ id : UUID
+ logement : Logement
+ émetteur : Utilisateur
+ destinataire : Utilisateur
+ contenu : text
+ dateEnvoi : datetime
+ lu : bool
```

---

### 🔹 `Commentaire`

```plaintext
+ id : UUID
+ logement : Logement
+ auteur : Client
+ note : int (1 à 5)
+ texte : text
+ datePublication : datetime
+ validéParAdmin : bool
```

---

### 🔹 `Fichier` (utilisé pour les photos et KYC)

```plaintext
+ id : UUID
+ url : string
+ nomFichier : string
+ type : string
+ dateUpload : datetime
```

---

## 🔁 **3. Relations**

* `Client` —< `Réservation` >— `Logement`
* `AgentImmobilier` —< `Logement`
* `Logement` —< `Disponibilité`
* `Réservation` —1→1— `Paiement`
* `Client` —< `Commentaire` >— `Logement`
* `Utilisateur` —< `Message` >— `Utilisateur`
* `Logement` —< `Fichier`
* `AgentImmobilier` —< `Fichier` (documents KYC)
