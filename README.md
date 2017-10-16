# APT_Mini-Project

# Hello, before deploy to the team gae, remember to change the google map key in the geoView.html.
# Also, delete all streams on our website, since we add longitude and latitude in Image, we need to re-create streams and upload images.

Be sure to modify the following files:
1.trending.py - Update5, UpdateHour, UpdateDay: change my email to other email
2.main,py - CreateStream - post: change my email to other email

FYI:
1.Haven't meet Pep8 style yet.
2.cron.yaml: used to tell gae to automately update things.(used for trending)
3.base.html: inlcudes top nav-bar, sign-off button, and css, so other html files only have use "extend base.html" to include the former things. It makes other html files cleaner lol.

When deploy, use:
"gcloud app deploy app.yaml index.yaml cron.yaml"
