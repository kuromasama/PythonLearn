import subprocess

while(1): 
    out=subprocess.call('tasklist |find /i"ScreenClippingHost.exe"',shell=True)
    out=subprocess.call('taskkill /f /im "ScreenClippingHost.exe"',shell=True)