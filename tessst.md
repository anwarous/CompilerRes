



#### Exrcice 1 : 

Écrire un algorithme qui demande à l’utilisateur de saisir un nombre de départ, puis affiche successivement les valeurs allant de ce nombre jusqu’à ce nombre augmenté de 10.

### **Exemple**

Si l’utilisateur saisit le nombre **5**, l’algorithme affichera : 5 ,6 ,7,8,9,10,11,12,13,14,15

``` 
Algorithme pour 
debut 
	Ecrire("donner n : ")
	Lire(n)
	pour i de n a n + 10 faire 
		Ecrire(i)
	fin pour 
fin 

Algorithme pour 
debut 
	Ecrire("donner n : ")
	Lire(n)
	ch <-- "" 
	pour i de n a n + 10 faire 
		ch <-- ch + convch(i)  
	fin pour 
	Ecrire(ch) // 10 11 12 13 14 15 16 17 18 19 20
fin 

```

| objet | type   |
| ----- | ------ |
| n     | entier |
| ch    | chaine |

#### Exercice 2 : 

Écrire un algorithme qui demande des nombres à l'utilisateur et les additionne. La saisie s'arrête quand l'utilisateur tape le nombre `0`. À la fin, affichez la somme totale.

```
Algorithme addition 
debut 
	s <-- 0 
	repeter
		Ecrire("donner un nombre : ")
		Lire(n)
		s <-- s + n 
	jusqu'a n = 0 
	Ecrire("somme = ", s )
fin 
```

| objet | type   |
| ----- | ------ |
| n     | entier |
| s     | entier |



#### Exercice 3 : 

```
Algorithme puissance 
debut 
	Ecrire("a : ")
	lire(a)
	Ecrire("b : ")
	Lire(b)
	p <-- 1 
	pour i de 1 a b faire 
		p <-- p * a 
	fin pour 
	Ecrire(a , "^" , b , " = " , p )
fin 
```

| objet | type   |
| ----- | ------ |
| a     | entier |
| b     | entier |
| p     | entier |



#### Exercice 4 : 

Écrire un algorithme qui  calcule puissance d'un entier 

###### example : 

a = 3 

b = 2 

puissance = 3 ^2 = 9 

```
Algorithme somme 
debut 
	s <-- 0 
	repeter 
		Ecrire("n : ")
		lire(n) 
    	si n MOD 2 = 0 alors 
    		s <-- s + n 
    	fin si 
    jusqu'a n = 0
    Ecrire(s)
fin
```

| objet | type   |
| ----- | ------ |
| s     | entier |
| n     | entier |

####  

#### Exercice 5 :

 Écrire un algorithme qui demande à l’utilisateur de saisir des nombres successivement.
 Le programme calcule la **somme des nombres pairs** saisis.
 La saisie s’arrête lorsque l’utilisateur entre le nombre **0**, et le programme affiche alors la somme obtenue.

```
Algprithme somme 
Debut 
	s <-- 0 
	repeter 
		Ecrire("n : ")
		Lire(n)
		si n Mod 2 != 0 alors 
			s <-- s + n 
		fin si 
	jusqu'a n = 0 
	Ecrire(s)
fin 
```

| objet | type   |
| ----- | ------ |
| s     | entier |
| n     | entier |



#### Exercice 5 : 

Écrire un algorithme qui gère un budget.
 Le programme demande d’abord à l’utilisateur de saisir un **budget initial**.
 Ensuite, il demande à chaque fois un **montant à retirer** :

- Si le montant est **supérieur au budget**, le programme affiche un **message d’erreur**.
- Sinon, le montant est **déduit du budget**.

Après chaque opération, le programme demande à l’utilisateur s’il souhaite **continuer ou arrêter**.
 Lorsque l’utilisateur choisit d’arrêter, le programme affiche le **budget restant**

```
Algorithme budget
debut 
	ecrire("budget = ")
	lire(budget )
	
	repeter 
		ecrire("montant ")
		lire(montant)
		si montant > budget alors 
			Ecrire("error ")
		sinon 
			budget <-- budget - montant 
		fin 
		Ecrire("continue ? (ok ou non )")
		Lire(msg )
	jusqu'a (msg = "non")
	Ecrire("budget restant : ", budget)
fin 
```

| objet   | type   |
| ------- | ------ |
| montant | entier |
| buget   | entier |

















































































































































































































































































































































