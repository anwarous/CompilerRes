



``` 
fonction contient_numero(mdp:chaine):booleen 
debut 
	v <-- faux 
	pour i de 0 a long(mdp)-1 faire
		si mdp[i]>="0" et mdp[i]<="9" alors
			v <-- vrai 
		fin si
	fin pour 
	retourner v 
fin


si majus(mdp)<"A" ou majus(mdp[i]) >"Z" ou non(contient_numero(mdp[i]]))
```











0							1							2							3	

| 2    | 3    | 6    | 5    |
| ---- | ---- | ---- | ---- |
| 4    | 8    | 5    | 9    |
| 5    | 8    | 3    | 0    |
| 1    | 2    | 4    | 11   |







```
pour i de 0 a ligne-1 faire 
	pour j de 0 a colone-1 faire
		Lire(M[i,j])
	fin pour 
fin pour 

```









```
Algorithme matrice 
debut 
Saisie(C,L)
	remplir(M,C,L)
	Ecrire("somme de matrice : ",sommeMat(M,C,L))
fin 

```



|                               |
| ----------------------------- |
| Mat = tableau de 20*20 entier |

| objet          | type      |
| -------------- | --------- |
| C,L            | entier    |
| M              | mat       |
| Saisie,remplir | procedure |
| sommeMat       | fonction  |
|                |           |

```
procdure Saisie(@C:entier,@L:entier)
debut 
	repeter 
		Ecrire("donner C : ")
		Lire(C)
	jusqu'a C > 0 
	
	repeter 
		Ecrire("donner L: ")
		Lire(L)
	jusqu'a L > 0
fin 
```



```
procedure remplir(@M:Mat,C,L:entier)
debut 
    pour i de 0 a ligne-1 faire 
        pour j de 0 a colone-1 faire
            Lire(M[i,j])
        fin pour 
    fin pour 
fin 
```



| objet | type   |
| ----- | ------ |
| i     | entier |
| j     | entier |

```
fonction sommeMat(M:Mat,C,L:entier):entier
debut 
	s <-- 0 
	pour i de 0 a L-1 faire 
		pour j de 0 C -1 faire 
			s <-- s+ M[i,j]
		fin pour 
	fin pour 
fin 
```

| objet | type   |
| ----- | ------ |
| i,j,s | entier |

```
procedure afficheMat(M:Mat,C,L:entier)
debut 
	pour i de 0 a L-1 faire 
		pour j de 0 a C-1 faire 
			Ecrire("M[",i,",",j,"]=",M[i,j])
		fin pour
	fin pour 
fin 

```

| objet | type   |
| ----- | ------ |
| i,j   | entier |





* Saisie ( C >5 et L > 6 )

* Remplir Matrice 

* affiche Matrice 

* Maximum Matrice 

* 

* 

  

 



* saisie ( C , L >0 C == L )

* remplir matrice ( entier positif !!! )
* somme diagonal ( i == j )

* afiicher Matrice 

| 1    | 2    | 3    | 4    |
| ---- | ---- | ---- | ---- |
| 5    | 6    | 7    | 8    |
| 9    | 10   | 11   | 12   |
| 0    | 2    | 4    | 1    |



















| 1    | 0    | 2    | 3    |
| ---- | ---- | ---- | ---- |
| 4    | 2    | 4    | 1    |
| 5    | 1    | 0    | 2    |
| 1    | 3    | 2    | 4    |
|      |      |      |      |





| 6    | 11   | 8    | 10   |
| ---- | ---- | ---- | ---- |



procedure Remplirtab(M:mat,L,C:entier , @t :tab , @n :entier )





