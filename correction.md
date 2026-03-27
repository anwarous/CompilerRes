



### exercice 18 : 

```
algorithme leaders 
debut 
	pour i de 0 a n-1 faire 
		Ecrire("T[",i,"]=")
		Lire(T[i])
	fin pour 
	ch <-- ""
	
	pour i de 0 a n-1 faire
    	j <-- i+1 
    	tant que t[i]>t[j] et j <= n-1 faire 
    		j <-- j+1 
    	fin tant que 
    	si j>n-1 alors
    		ch <-- ch + " " + t[i]
    	fin si 
    fin pour 
    ecrire(ch)
fin 
```

|                             |
| --------------------------- |
| tab = tableau de 100 entier |

## Exercice 19 

```

j<-- 0 
k <-- 0 
pour i de 0 a n+m faire 
	si j<n et k < m alors 
		si t1[j]<t2[k] alors 
			c[i] <-- t1[j]
			j <-- j + 1 
		sinon 
			c[i] <-- t2[k]
			k <-- k + 1 
		fin si 
	sinon si j<n alors
		c[i] <-- t1[j]
		j <-- j + 1 
	sinon 	
		c[i] <-- t2[k]
		k <-- k + 1 
	fin si 
fin pour 
```









```
Algorithme sommeChiffre
prog princ
debut
	saisie(n)
	s <-- sommeChiffre(n)
	Ecrire(s)
fin 


```

| objet        | type      |
| ------------ | --------- |
| n            | entier    |
| s            | entier    |
| saisie       | procedure |
| sommeChiffre | fonction  |

```
procdeure saisie( @n : entier )
debut 
	repeter 
		Ecrire("donner n : ")
		lire(n)
	jusqu'a n >0 
fin

fonction sommeChiffre(n:entier):entier 
debut 	
	s <-- 0 
	tant que n !=0 faire 
		s <-- s + n MOD 10 
		n <-- n DIV 10 
	fin tant que 
	retourner s 
fin 
```

| objet | type   |
| ----- | ------ |
| s     | entier |
|       |        |









* saisie N (5>N>15)

* remplir l tableau N entier 

* max 

* min 

* somme 

* afficher res 

  ```
  Algorithme tableau 
  prog princ 
  	saisie(n)
  	remplir(T,n)
  	m <-- max(T,n)
  	mi <-- min(T,n)
  	s <-- somme(T,n)
  	afficher(m,mi,s,T,n)
  fin 
  ```

  |                            |
  | -------------------------- |
  | tab = tableau de 15 entier |

  | objet           | type      |
  | --------------- | --------- |
  | n               | entier    |
  | t               | tab       |
  | m,mi,s          | entier    |
  | saisie,afficher | procedure |
  | max,min,somme   | fonction  |
  |                 |           |
  |                 |           |
  |                 |           |
  |                 |           |
  |                 |           |
  |                 |           |

  



```
procedure saisie(@n:entier)
debut
	
	repeter 
		Ecrire("donner n : ")
		Lire(n)
	jusqu'a n >5 et n < 15 

fin

procedure remplir(@T:tab,n:entier )
debut 
	pour i de 0 a n-1 faire 
		ecrire("T[",i,"]=")
		lire(t[i])
	fin pour 
fin 
```

| objet | type   |
| ----- | ------ |
| i     | entier |

```

```























































































































































