# `virtualenv` instructions

Tutorial how to run this script in an virtual python environment on your computer.

(*If you want to learn more visit [this](http://docs.python-guide.org/en/latest/dev/virtualenvs/) or [this](https://virtualenv.pypa.io/en/stable/userguide/) site*)

## 1. Install `virtualenv`

```
$ pip install virtualenv
```

Test your installation:

```
$ virtualenv --version
```

*If it doesn't work (bash doesn't know this command make sure you have installed python and try this: https://stackoverflow.com/a/41429177/7827128*

## 2. Create a virtual environment

Go into a directory where you want to place the virtual environment and enter:

```
$ virtualenv project_name
```

This will create a virtual environment in the new created folder `project_name`.

## 3. Copy files

Now copy all the files (or the whole folder) in this new directory `project_name`.

**Be sure that you edit all paths to this new path!!**

## 4. Activate the virtual environment

Now lets's activate the virtual environment.

Go into the folder `project_name` and enter:

```
$ source bin/activate
```

You should see `(project_name)` at the left of your terminal. 

## 5. Install requirements/packages

Before you can run the project you need to install the required packages (because the virtual environment has no packages besides the default packages installed).

This can be achieved by installing the packages that are listed in the `requirements.txt` file over this command:

```
$ pip install -r requirements.txt
```

*If you copied the folder you obviously need to enter it `cd folder_name` that the path to the file `requirements.txt` is right.*

## 6. Run the script

If you did everything and changed all paths to the new path of the virtual environment you should now be good to go and able to run this python script!



Have fun programming!



## 7. Exit the virtual environment

If you want to exit the virtual environment and get back to your system just type:

```
$ deactivate
```

## 8. Export used packages

If you want that others also can run this script on their computers using `virtualenv` run this command:

```
$ pip freeze > requirements.txt
```

And upload the file with your script so that everyone can simply install via step 5 all required packages.

## 9. Remove it

Just `deactivate` it like in step 8 and remove the whole directory. Now it's deleted.