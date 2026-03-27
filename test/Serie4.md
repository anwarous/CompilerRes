#### Exercise 1 : 



    Algorithme inverse 
    Début
        Écrire("Entrez un nombre : ")
        Lire(n)
        inverse <- 0
        TantQue (n > 0) Faire
            reste <- n Mod 10
            inverse <- (inverse * 10) + reste
            n <- n Div 10
        FinTantQue
    
        Écrire("Sortie : ", inverse)
    fin
| objet   | type   |
| ------- | ------ |
| n       | entier |
| reste   | entier |
| inverse | entier |

#### Exercise 2 :  

```
Algorithme Parite_Signe

Début
    Écrire("Entrez un entier : ")
    Lire(n)
    Si (n Mod 2 = 0) Alors
        Si (n >= 0) Alors
            Écrire("Pair et Positif")
        Sinon
            Écrire("Pair et Négatif")
        FinSi
    Sinon
        Si (n >= 0) Alors
            Écrire("Impair et Positif")
        Sinon
            Écrire("Impair et Négatif")
        FinSi
    FinSi
Fin
```

| objet | type   |
| ----- | ------ |
| n     | entier |

#### Exercise 4 : 

```
Algorithme Puissance
Début
    Écrire("Saisissez X : ")
    Lire(X)
    Écrire("Saisissez n (entier positif) : ")
    Lire(n)
    
    resultat <- 1
    Pour i de 1 à n Faire
        resultat <- resultat * X
    FinPour
    
    Écrire("Sortie : ", resultat)
Fin
```

| objet    | type   |
| -------- | ------ |
| X        | reel   |
| resultat | reel   |
| n        | entier |
| i        | entier |

#### Exercise 5 : 

```
Algorithme Multiples_de_7
Début
    Écrire("Les multiples de 7 entre 1 et 200 sont :")
    Pour i de 7 à 200 Faire
        Écrire(i)
    FinPour
Fin
```

| objet | type   |
| ----- | ------ |
| i     | entier |

#### exercise 6 : 

```
Algorithme Moyenne_Classe
Début
    somme <- 0
    compteur <- 0
    
    Pour i  de 1 à 10 Faire
        Écrire("Entrez la note ", i, " : ")
        Lire(notes[i])
        somme <- somme + notes[i]
    FinPour
    
    moyenne <- somme / 10
    
    Pour i  de 1 à 10 Faire
        Si (notes[i] > moyenne) Alors
            compteur <- compteur + 1
        FinSi
    FinPour
    
    Écrire("Moyenne : ", moyenne)
    Écrire("Nombre de notes supérieures à la moyenne : ", compteur)
Fin
```

| objet    | type   |
| -------- | ------ |
| notes    | tab    |
| somme    | reel   |
| moyenne  | reel   |
| i        | entier |
| compteur | entier |
|          |        |

##### TDNT 

| type                       |
| -------------------------- |
| tab =  tableau de 100 reel |

#### Exercise 7 : 

```
Algorithme Max_Min_Tableau

Début

    Pour i  de 1 à 20 Faire
        Écrire("Entrez l'entier n°", i, " : ")
        Lire(T[i])
    FinPour
    

    max <- T[1]
    min <- T[1]
    
    Pour i  de 2 à 20 Faire
        Si (T[i] > max) Alors
            max <- T[i]
        FinSi
        
        Si (T[i] < min) Alors
            min <- T[i]
        FinSi
    FinPour
    
    Écrire("Valeur maximale : ", max)
    Écrire("Valeur minimale : ", min)
Fin
```

| objet | type   |
| ----- | ------ |
| T     | tab    |
| i     | entier |
| min   | entier |
| max   | entier |
|       |        |

##### TDNT 

| type                       |
| -------------------------- |
| tab = tableau de 20 entier |

