"""
Test for Mie theory main FORTRAN code converted to python script 
"""


import numpy as np
from dimpy import *
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
P,Q,R,C,S,AR,AI,BR,BI=dim(21001),dim(21001),dim(21001),dim(21001),dim(21001),dim(21001),dim(21001),dim(21001),dim(21001)
f1 = open(os.path.join(script_dir, "mie1.out"), "w")
f2 = open(os.path.join(script_dir, "mie2.out"), "w")
f3 = open(os.path.join(script_dir, "simulation.out"), "w")
SSS1=0.0
SSS2=0.0
NMAX=21001
a=100
AMU1=1.5
AMU2=0.0
WL=6.283185307
DK=0.1
for ITH in range (1,181,2):
    X=(6.283185307*a)/WL
    Y1=X*AMU1
    Y2=-X*AMU2
    YY=Y1*Y1+Y2*Y2
    NYY=int(1.01*np.sqrt(YY)+50.0)
    if AMU1 - 1.0 < 0:
        NYY = NYY + int(X * (1.0 - AMU1))
    else:
        NX = NYY
    if(NYY-NMAX)<=0:
        if(NYY-0.10E-09)<=0:
            N=NYY+int(0.75*X+50.0)
        else:
            N=NX+int(0.75*X+50.0)
    else:
        NX=NMAX
    PJN1=0.0
    QJN1=0.0
    RJN1=0.0
    CX=np.cos(X)
    SX=np.sin(X)

    C[0]=(CX/X)+SX
    CQ=CX/C[0]
    JN=N+1
    while True:  # Label 35
        JN=JN-1
        XN=2*JN+1
        PR=(XN*Y1/YY)-PJN1
        PI=(XN*Y2/YY)+QJN1
        PP=PR*PR+PI*PI
        RJN=X/(XN-X*RJN1)
        PJN=PR/PP
        QJN=PI/PP
        #print(PJN,QJN,RJN)
        if (JN - NMAX) <= 0:
            P[JN-1] = PJN
            Q[JN-1] = QJN
            R[JN-1] = RJN
        else:
            PJN1 = PJN
            QJN1 = QJN
            RJN1 = RJN
        if (JN - 1) <= 0:
            break
    TXE=0.0
    SCA=0.0
    ASQ=0.0
    for NS in range(1, NMAX+1): # do 10 NS=1,NX
        CN=NS
        if (NS-1) <= 0:
            S[0]=(SX/X)-CX
            DCX=CX-C[1]/X
        else:
            S[NS-1]=R[NS-1]*S[NS-2]
            XN=2*NS-1
            QC=X/(XN-X*CQ)
            C[NS-1]=C[NS-2]/QC
            DCX=C[NS-2]-CN*(C[NS-1]/X)
            CQ=QC
        PQ=(P[NS-1]**2)+(Q[NS-1]**2)
        #print(P[NS-1],Q[NS-1])
        ZR1=(P[NS-1]/PQ)-CN*(Y1/YY)
        ZI1=CN*(Y2/YY)-Q[NS-1]/PQ
        X1=(1.0/R[NS-1])-CN/X
        ZR2=1.0
        ZI2=C[NS-1]/S[NS-1]
        ZR3=X1
        ZI3=DCX/S[NS-1]
        ANR=ZR1-X1*AMU1
        ANI=ZI1+X1*AMU2
        ADR=ZR1-ZI1*ZI2-AMU1*X1-AMU2*ZI3
        ADI=ZR1*ZI2+ZI1-AMU1*ZI3+AMU2*X1
        BNR=AMU1*ZR1+AMU2*ZI1-X1
        BNI=AMU1*ZI1-AMU2*ZR1
        XR=ZR1-ZI1*ZI2
        XI=ZR1*ZI2+ZI1
        BDR=AMU1*XR+AMU2*XI-ZR3
        BDI=AMU1*XI-AMU2*XR-ZI3
        AA=(ADR**2)+(ADI**2)
        ARNS=(ANR*ADR+ANI*ADI)/AA
        AINS=(ANI*ADR-ANR*ADI)/AA
        BB=(BDR**2)+(BDI**2)
        BRNS=(BNR*BDR+BNI*BDI)/BB
        BINS=(BNI*BDR-BNR*BDI)/BB
        AR[NS-1]=ARNS
        AI[NS-1]=AINS
        BR[NS-1]=BRNS
        BI[NS-1]=BINS
        RN=CN+0.5
        TXE=TXE+RN*(ARNS+BRNS)
        SCA=SCA+RN*(ARNS**2+AINS**2+BRNS**2+BINS**2)
        TEST=RN*(ARNS+BRNS)/TXE
        TEST=TEST**2
        if (NS-1)<=0:
            VAPISR=1.5*(BR[0]-AR[0])
            VAPISI=1.5*(BI[0]-AI[0])
        else:
            FNPV=CN-1.0
            FNA=FNPV*(CN+1.0)/CN
            FNB=(FNPV+CN)/(FNPV*CN)
            ASQ=ASQ+(AR[NS-2]*AR[NS-1]+AI[NS-2]*AI[NS-1])*FNA
            ASQ=ASQ+(BR[NS-2]*BR[NS-1]+BI[NS-2]*BI[NS-1])*FNA
            ASQ=ASQ+(AR[NS-2]*BR[NS-2]+AI[NS-2]*BI[NS-2])*FNB
            RM=RN*((-1.0)**NS)
            VAPISR= VAPISR+RM*(AR[NS-1]-BR[NS-1])
            VAPISI= VAPISI+RM*(AI[NS-1]-BI[NS-1])
            if (TEST-0.1E-21)<=0:
                break
    XX=4.0/(X*X)
    QEXT=XX*TXE
    QSCA=XX*SCA
    QABS=QEXT-QSCA
    ALBED=QSCA/QEXT
    RHO=2.0*X*(AMU1-1.0)
    ASQ=XX*ASQ
    ASYM=ASQ/QSCA
    QPR=QEXT-ASQ
    QBAK=XX*((VAPISR**2)+(VAPISI**2))
    NN=CN
    TH=ITH-1
    THETA=TH
    TH=TH*0.01745329
    CTH=np.cos(TH)
    PI=0.0
    PI1=1.0
    S1R=1.5*(AR[1]+CTH*BR[1])
    S1I=1.5*(AI[1]+CTH*BI[1])
    S2R=1.5*(AR[1]*CTH+BR[1])
    S2I=1.5*(AI[1]*CTH+BI[1])
    for M in range(2,NN+1):
        FN=M
        FNN=(2.0*FN+1.0)/(FN*(FN+1.0))
        PI2=(CTH*(2.0*FN-1.0)*PI1-FN*PI)/(FN-1.0)
        TAU2=FN*CTH*PI2-(FN+1.0)*PI1
        S1R=S1R+FNN*(AR[M-1]*PI2+BR[M-1]*TAU2)
        S1I=S1I+FNN*(AI[M-1]*PI2+BI[M-1]*TAU2)
        S2R=S2R+FNN*(AR[M-1]*TAU2+BR[M-1]*PI2)
        S2I=S2I+FNN*(AI[M-1]*TAU2+BI[M-1]*PI2)
        PI=PI1
        PI1=PI2
    SS1=(S1R**2)+(S1I**2)
    SS2=(S2R**2)+(S2I**2) 
    TSS=SS1+SS2
    Pg=2*TSS/(QSCA*(X**2))
    if a<0.62:
        TT=-2
    elif a>6.2:
        TT=-3.4
    else:
        TT=-2.5
    U=a**TT
    SSS1=U*SS1*DK+SSS1
    SSS2=U*SS2*DK+SSS2  
#       write(*,*) theta,tss,x,qsca,pg
#      write(3,*)theta,ss1,ss2,tss
    f2.write(f"{THETA} {Pg}\n")
    POLAR=(SS1-SS2)/TSS
#    SS=0.5*SS
    f2.write('The values of X,THETA,SS1,SS2,POLAR are\n')
    f2.write(f"{X} {THETA} {SS1} {SS2} {POLAR}\n")  
    SPOL=(SSS1-SSS2)/(SSS1+SSS2) 
    f1.write(f'{THETA} {POLAR}')
    SSS1=0.0
    SSS2=0.0
print('X,qsca,QEXT,QABS,ALBED,ASYM,QPR,QBAK,NN are')
print(X,QEXT,QABS,ALBED,ASYM,QPR,QBAK,NN)
f1.close()
f2.close()
f3.close()