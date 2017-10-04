# APT_Mini-Project

Hi all, I've tried to combine all things together.
You can now clone the whole repo and upload to your own app engine to test.
It surely works now but still need to be tested, so try to create lot of streams and upload some images. Also try to use trending report and subcribe.

Be sure to modify the following files:
1.trending.py - Update5, UpdateHour, UpdateDay: change my email to other email
2.main,py - CreateStream - post: change my email to other email

FYI:
1.Haven't meet Pep8 style yet.
2.cron.yaml: used to tell gae to automately update things.(used for trending)
3.base.html: inlcudes top nav-bar, sign-off button, and css, so other html files only have use "extend base.html" to include the former things. It makes other html files cleaner lol.

