# Music and Technology II project (Spring 2021)
## Summary
Sonifying and spatializing _Super Smash Bros. Melee_ to make it accessible to those who are blind.

## Necessary Python packages and Pure Data externals
### Python
The Python code imports the following APIs:
* melee   (GitHub: https://github.com/altf4/libmelee/)
* pyOSC3  (GitHub: https://github.com/Qirky/pyOSC3/)

Both can be installed through pip.

### Pure Data
The main patch uses vanilla Pure Data with the following externals:
* iemnet
* osc
* vstplugin~

These can be installed through Deken, the built-in package manager. (On the Pd menu bar, click on "Help" and then "Find externals". Make sure to include the tilde when searching for vstplugin~.)
