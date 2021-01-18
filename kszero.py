#! /usr/bin/env python3
import pandas as pd
import scipy
import numpy as np
from scipy import interpolate
from scipy import optimize
from collections import defaultdict
import os
import argparse


def main():
    parser=argparse.ArgumentParser(description="Takes input 2 column (tab sep) list, expicitly titled 'kszero.inp'. Left column is temperatures (K), Right column is the [back FFT] k-space data file names that must be in data/ subidrectory (canot be binary).")
    parser.add_argument("-f",help="Data to input filename" ,dest="input_data", type=str, required=False, default="kszero.inp")
    parser.add_argument("-w",help="Region for zeros to be extracted, three numbers seperated by space i.e. (<low zero> <high zero> <number of crossings>)",nargs=3,action='append',dest="window",required=True)
    parser.set_defaults(func=run)
    args=parser.parse_args()
    args.func(args)


#-----------------------------------------------------------------------------------------------
class KData:

    def __init__(self, datarg, region):
        self.filename= './data/'+str(datarg)

        self.zero_init=np.linspace(float(region[0][0]),float(region[0][1]),int(region[0][2]))
        
    def headread(self):
        kz_cross=[]
        with open(self.filename) as myfile:
            head = [next(myfile) for x in range(40)]
            self.hd_len=pd.Series(head).str.contains('#').sum()
    def framed(self):
        self.df=pd.read_csv(self.filename,skiprows=self.hd_len,sep="\s+")
        return self.df
    def plot(self,t=0):
        df=self.df
        plt.plot(df[df.columns[0]],df[df.columns[1]],label="T= "+str(t))
        plt.legend()
    def find_zeroes(self):
        af=self.df
        br_xin=self.zero_init
        soft_low=0.8*min(br_xin)
        soft_max=1.2*max(br_xin)
        af=af[af[af.columns[0]]>soft_low]
        af=af[af[af.columns[0]]<soft_max]
        
        func=interpolate.interp1d(af[af.columns[0]],af[af.columns[1]])
        z=optimize.fsolve(func, br_xin)
        return z
        
def process(datals,temps,est):
    
    kzs=defaultdict()
    for temp,filename in zip(temps,datals):
        spec=KData(filename,est)
        spec.headread()
        spec.framed()
        kzs[temp]=spec.find_zeroes()

    return kzs
       

def run(args):
    
    input_file=args.input_data
    zero_estimates=args.window
    
    df=pd.read_csv(input_file,header=None, sep='\s+')
    datals=list(df[1])
    temps=list(df[0])
    
    kn=defaultdict()
    kzs=process(datals,temps,zero_estimates)
    dd=pd.DataFrame.from_dict(kzs)
    for c in dd.columns:
        outf=dd[[10,c]]
        outf[c]=outf[c]-outf[10]
        outf.to_csv(str(datals[0].split('.')[0])+'_'+str(c)+'kzero.dat',header=None,index=None, sep=' ')

    return kzs



if __name__ == '__main__':
    main()

