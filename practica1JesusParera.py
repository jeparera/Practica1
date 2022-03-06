"""
@author: Jesús Parera
"""
from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Array
from time import sleep
import random
"""
He cogido la plantilla de productor-consumidor del campus la cual he modificado.
El programa funciona de la siguiente manera: storage es un array compartido tal que tiene tantos elementos como 
productores hay. Cada productor tiene asignado un lugar en el array dado por su número. Una vez los productores
han añadido un número al array, el consumidor escoge el menor y manda una señal al productor que lo envió para 
que añada otro número.
"""
M =500 #Máximo número al que pueden llegar los productores.#
N = 4 #Número de números que generan los productores.#
NPROD = 4 #Número de productores.#

def delay(factor = 3):
    sleep(3/factor)

def add_data(storage, data, mutex,posicion):
    mutex.acquire()
    try:
        storage[posicion] = data #Añade el número en la posición que corresponde al productor.#
        delay(15)
    finally:
        mutex.release()


def get_data(storage, mutex):
    mutex.acquire()
    try:
        x = M+1 #Los números producidos nunca son mayores de M.#
        posicion = 0
        posdef = 0
        for i in storage: #Este bucle recorre el array y se queda con el menor número y su posición.(Siempre y cuando sean diferentes de -1)#
            if i<x and i !=-1:
                x = i
                posdef = posicion
            posicion = posicion + 1
        data = [x,posdef]
    finally:
        mutex.release()
    
    return (data) #Devolvemos el menor y su posición en el array.#


def producer(storage, empty, non_empty, mutex,posicion):
    numero = 1
    for i in range(N): #Generamos N números por productor.#
        numero = random.randint(numero,M) #Genera un número aleatorio mayor o igual al anterior.#
        empty.acquire() #Semáforo que deja proceder si se ha cogido el número de ese productor.#
        add_data(storage,numero, mutex,posicion)#Añadimos el número al array.#
        print (f"producer {current_process().name} almacenado {numero}")
        non_empty.release()#Avisamos de que ya hemos metido el número.#
    #Por último añadimos un -1#
    empty.acquire()
    add_data(storage,-1, mutex, posicion)
    non_empty.release()
    
def consumer(storage, empty, non_empty, mutex,definitiva):
    for i in non_empty: #Esperamos que todos los productores hallan metido un n�mero.#
        i.acquire()
    while (len(definitiva)!=(NPROD*N)): #Cogemos todos los numeros que se producen.#
        
        dato = get_data(storage, mutex)#Escogemos el menor#
        definitiva=definitiva+[dato[0]]#Añadimos el menor a la lista.#
        print (f"{current_process().name}:: Tenemos:", storage[:],"cogemos el dato del productor",dato[1],"y queda:", definitiva)
        empty[dato[1]].release()#Llamamos al semáforo del productor el cual hemos cogido el número.#
        non_empty[dato[1]].acquire() #Dejará continuar cuando el productor que está metiendo el número termine. #
        delay()
    print("La lista final queda:",definitiva) #Solucion final.#

def main():
    storage = Array('i', NPROD) #Array con los mismos elementos que el número de productores.#
    for i in range(NPROD):#Empieza con -1s.#
        storage[i] = -1
    print ("almacen inicial", storage[:])
    non_empty=[]
    for i in range(NPROD):  
        non_empty = non_empty + [Semaphore(0)] #Sem�foro para que cada productor avise al consumidor.#
    empty=[]
    for i in range(NPROD):  
        empty = empty + [BoundedSemaphore(1)] #Cada semáforo correspoderá a un productor.#
    mutex = Lock() #Semáforo para trabajar con el array y evitar problemas.#

    prodlst = [ Process(target=producer,
                        name=f'prod_{i}',
                        args=(storage, empty[i], non_empty[i], mutex,i))
                for i in range(NPROD) ]#A cada productor le pasamos su semáforo correspondiente.#

    conslst = [ Process(target=consumer,
                      name="consumidor",
                      args=(storage, empty, non_empty, mutex,[]))]#Al consumidor le pasamos la lista con todos los semáforos.#

    for p in  conslst + prodlst: #Iniciamos los procesos.#
        p.start()

    for p in prodlst + conslst: #Finalizamos los procesos.#
        p.join()


if __name__ == '__main__':
    main()
