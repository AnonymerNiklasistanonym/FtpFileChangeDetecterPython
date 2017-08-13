# FtpFileChangeDetecterPython
Check your FTP files on changes without even downloading them. Very fast because of only the modified date gets compared in the first place.

# Important
This script was developed for the `CRON` task scheduler.

Install the simple GUI with this command:
```
sudo apt-get install gnome-schedule
```
And open it with the command:
```
gnome-schedule
```
Now copy all files of this repository on your computer.

* Insert your own FTP credentials in `crredentials_ftp.json`
* Insert your own paths to your FTP files in `watch_these_ftp_files.json`
* Inser the path where the file `script.py` in `script.py` (at the begin - look into the comments)

Then create a new `CRON` task over the GUI with the command
```
python <path to the script.py file>
```
Then choose your desired time the script should be executed and save everything.

# But what does it do
The script checks if the modified time of an FTP file is new (in compariston to the last crawl).
If yes it downloads the new file and updates the modified date in the *"_time.json"* file.

# License

This repository is under the MIT license - that means you can do what you want with this script.

But if you have a cool idea or any kind of improvement suggestion let me know it :smiley:
