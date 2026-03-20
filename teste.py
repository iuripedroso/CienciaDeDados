import numpy as np

# criação 1D

vetor = np.arange(9)

# matriz booleana 3x3 

vetor2 = np.ones((3,3) ,dtype = bool)

# extrair impares

print(vetor[ vetor % 2 != 0])

# substituir impares 

svetor = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

svetor[svetor % 2 != 0] = -1

print (svetor)

# matriz aleatoria

matriz = np.random.randint(0, 10, size=(3, 3))

print(matriz)

# soma de array

print(matriz.sum(axis=0) )