import random
import math
import queue 

def exponential(lmda):
    val = random.random()
    return -1/lmda * (math.log(val))

def normal01():
    y = 0
    while True:
        y1 = exponential(1)
        y2 = exponential(1)
        y = y2 - (y1 - 1)**2/2
        if y > 0:
            break
    u = random.random()
    return y if u <= 1/2 else -1 * y 

def normal(miu, ro):
    return normal01() * math.sqrt(ro) + miu

def generate_client_type():
    u = random.random()
    if u <= 0.45:
        return 1
    elif 0.45 < u <= 0.7:
        return 2
    elif 0.7 < u <= 0.9:
        return 4
    return 3

def generate_client(t, lmda):
    #return t - 1/lmda*(math.log(random.random()))   
    return t + exponential(lmda)

class HappyComputing:
    def __init__(self, uptime, vendors, tec, stec, arrival ,vendor_lambda, tec_lambda, stec_lambda, infinite=None):
        self.T = uptime #Shop working time
        self.n_vendors = vendors #Number of vendors
        self.n_tec = tec # tecs number
        self.n_stec = stec # special tecs number
        self.arrival = arrival # lamda of arrival time
        self.infinite = 2*self.T if infinite is None else infinite # Considerable large number to avoid errors
        self.reset() 
        

    def reset(self):
        self.SS = [0] * (self.n_vendors + 1) # Sistem state [0] number of costumers in the system, [i] i>0 costumer with vendor i
        self.EL = [ self.infinite ] * (self.n_vendors + 1) #Event list [0] next arrival [i] i>0 service completion time of vendor i
        self.CS = [0] * self.n_vendors #Number of costumers served by each vendor
        self.A = [] #arrival time of costumers
        self.D = [] #depature time of costumers 
        self.Tp = 0 #Time after work sesion limit
        self.t = 0 #Simulation time
        self.NA = 0 #Arrival count
        self.ND = 0 #Depature count

    def simulate(self):
        self.reset()
        self._simulate()

    def _simulate(self):
        #Generar el 1mer cliente
        i = 5
        self.EL[0] = generate_client(self.t, self.arrival)
        #self.A.append((1, self.EL[0]))
        while(True):
            if not i:
                break
           # i -= 1
            ta = self.EL[0]
            ti = min(*self.EL)
            T = self.T
            n = self.SS[0]
            if ta == min(*self.EL) and ta <= T:
                #a new customer arrives
                self.t = ta
                self.NA += 1
                #print(f"Customer {self.NA} arrives at {self.t}")
                self.A.append((self.NA, self.t))
                # generar el próximo cliente
                self.EL[0] = generate_client(self.t, self.arrival)
                if self.EL[0] > T:
                    self.EL[0] = self.infinite
                #agregarlo a un vededor si es posible
                free = self._find_free_vendor()
                if free:
                    choice = random.choice(free)
                    #print(f"{choice} va a atender al cliente {self.NA}")
                    self.SS[choice] = self.NA
                    self.EL[choice] = self.t + self._generate_vendor_time()
                    #print(f"{self.NA} se retira en el momento {self.EL[choice]}")
                self.SS[0] += 1
                continue
            elif ti < self.infinite and ta != ti:
                #a customer leaves
                # _min es el indice del servidor que termina antes
                _min = [i for i in range(1,len(self.EL)) if self.EL[i] == ti][0]
                #print(f"Customer {self.SS[_min]} will leave at {ti}")
                self.t = ti
                self.CS[_min-1] += 1
                self.ND += 1
                #self.D[_min-1] = self.t
                self.EL[_min] = self.infinite
                self.SS[_min] = 0
                # there are customers waiting
                if n > self.n_vendors:
                    self.SS[_min] = max(*self.SS[1:]) + 1
                    self.EL[_min] = self.t + self._generate_vendor_time()
                self.SS[0] -= 1 
            else:
                break
        

            # elif min(*self.EL) < self.infinite:
            #     #No more arrivals.
                



    def _find_free_vendor(self):
        return [ i for i in range(1,len(self.SS)) if self.SS[i] == 0 ]
    
    def _generate_vendor_time(self):
        return abs(normal(5,2))


a = HappyComputing(480, 2, 1, 1,1/20, 20, 20,15, 9999999999)

a.simulate()

print(a.A)