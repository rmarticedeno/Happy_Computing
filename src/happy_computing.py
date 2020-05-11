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
        self.SS = [0] * (self.n_vendors + self.n_tec + self.n_stec + 1) # Sistem state [0] number of costumers in the system, 
        # [i] in [1, self.n_vendor + 1] (vendors), i in [self.n_vendors + 2, self.n_vendors + self.n_tex + 2] (tecs), rest (spec tecs)
        self.EL = [ self.infinite ] * (self.n_vendors + self.n_tec + self.n_stec + 1) #Event list [0] next arrival [i] i>0 service completion time of vendor i
        self.CS = [0] * self.n_vendors #Number of costumers served by each vendor
        self.A = [] #arrival time of costumers
        self.D = [] #depature time of costumers 
        self.Tp = 0 #Time after work sesion limit
        self.t = 0 #Simulation time
        self.NA = 0 #Arrival count
        self.ND = 0 #Depature count
        self.profit = 0 #earnings of the day
        self.Stec = queue.Queue() # Special Tec waiting queue
        self.Tec = queue.Queue() # Regula Tec waiting queue

    def simulate(self):
        self.reset()
        self._simulate()

    def _simulate(self):
        #Generar el 1mer cliente
        self.EL[0] = generate_client(self.t, self.arrival)
        while(True):
            ta = self.EL[0]
            tv = min(*self.EL[1:self.n_vendors + 1])
            ttec = min(*self.EL[self.n_vendors + 1: self.n_vendors + self.n_tec + 1])
            tstec = min(*self.EL[self.n_vendors + self.n_tec + 1:])
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
                free = self._find_free_worker()
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
                self.D.append((self.SS[_min], ti))
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
                



    def _find_free_worker(self, s_type = 0):
        _min = 1
        _max = self.n_vendors + 1
        if s_type:
            _min += self.n_vendors
            _max += self.n_tec
            if s_type > 1:
                _min += self.n_tec
                _max += self.n_stec
                
        return [ i for i in range(_min,_max) if self.SS[i] == 0 ]

    def _route_client(self, id, _vendor_time):
        _type = generate_client_type()

        if _type == 4:
            self.profit += 750
            self.D.append((id, _vendor_time))
        elif _type == 3:
            stec = self._find_free_worker(s_type=2)
            if stec:
                choice = random.choice(stec)
                # generate time
                # add to SS variable
            else:
                self.Stec.put_nowait((id, _vendor_time, _type))
        else:
            tec = self._find_free_worker(s_type=1)
            if tec:
                choice = random.choice(tec)
                # generate time
                # add to SS variable
            else:
                stec = self._find_free_worker(s_type=2)
                if stec:
                    choice = random.choice(stec)
                    # generate time
                    # add to SS variable
                else:
                    self.Tec.put_nowait((id, _vendor_time, _type))



    def _generate_vendor_time(self):
        return abs(normal(5,2))


a = HappyComputing(480, 2, 1, 1,1/20, 20, 20,15, 9999999999)

a.simulate()

print(a.A)
print(a.D)