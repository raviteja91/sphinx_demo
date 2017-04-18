import os
giturl = raw_input("enter your GIT url:")
try:
	os.system("git clone " + giturl)
	print "cloned successfully..."
except Exception as err:
	print err.message
	print "cloning failed"
projectdir = raw_input("enter your project directory name:")
olddir = os.getcwd()
os.chdir(os.getcwd()+ "\\" + projectdir)
print os.getcwd()
os.system("git branch -a")
branch = raw_input("enter your branch name:")
try:
	os.system("git checkout " + branch)
	#print "switched to branch " + branch
except Exception as err:
	print err.message
	print "can't find your branch."
outputdir = raw_input("enter a name for output directory:")
os.system("sphinx-apidoc -F -o " + outputdir + " " + olddir)
os.system(outputdir + "\make.bat html")
