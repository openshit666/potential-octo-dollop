from pls import getpls

path = '/pls/wdm.pls'
print(path.split('/')[-1].replace('.pls', ''))
print(getpls(path.split('/')[-1].replace('.pls', '')).joinedpls.split('\n')[1].replace('file1=', ''))