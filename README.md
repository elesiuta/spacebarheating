# Spacebar Heating
A stupid script inspired by https://xkcd.com/1172/  
![https://xkcd.com/1172/](https://imgs.xkcd.com/comics/workflow.png "There are probably children out there holding down spacebar to stay warm in the winter! YOUR UPDATE MURDERS CHILDREN.")  
I never thought I'd have an actual use case for this, but here I am, fixes the LCD on my laptop which displays vertical lines when the temperature is cold.  
- clone the repo and install with  
`python setup.py install --user`
  - you may need to add [userbase](https://docs.python.org/3/library/site.html#site.USER_BASE) to PATH on Windows (or just install without `--user`)  
  - uninstall with `pip uninstall spacebarheating`  
- then start with  
`spacebarheating start`
- holding spacebar for 2.5 seconds will now max out your CPU usage until you release it
- you can stop the background process with  
`spacebarheating stop`
- you can also run the python script directly without installing via  
`python spacebarheating.py start|stop|version`
  - depends on installing https://pypi.org/project/keyboard/  

This software comes with ABSOLUTELY NO WARRANTY.
