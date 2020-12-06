import pandas as pd
import matplotlib.pyplot as plt

log = open('fahtemp.log','r')
df = pd.read_csv(log)
df.columns = ["date","temp","target","status"]
df['date'] = pd.to_datetime(df['date'],unit='s')
df['date'] = df['date'].dt.tz_localize('UTC').dt.tz_convert("America/Chicago")

##df['temp']=df['temp'].rolling(21,min_periods=1).mean()

fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_ylim(0,90)

next_color = "r"
for n in range(len(df['status'])-1):
    if df['status'].loc[n]==" FAH is running" and df['status'].loc[n+1]==" FAH is not running":
        x = [df['temp'][n],df['temp'][n+1]]
        y = [df['date'][n],df['date'][n+1]]
        
        plt.plot(y,x,c='r')
        next_color = "b"
        
    elif df['status'].loc[n]==" FAH is not running" and df['status'].loc[n+1]==" FAH is running":
        x = [df['temp'][n],df['temp'][n+1]]
        y = [df['date'][n],df['date'][n+1]]
        
        plt.plot(y,x,c='b')
        next_color = "r"
        
    else:
        x = [df['temp'][n+1],df['temp'][n]]
        y = [df['date'][n+1],df['date'][n]]
        plt.plot(y,x,c=next_color)


plt.plot(df['date'],df['target'],color='black')
plt.tight_layout()     
plt.show() 