curl -F 'access_token=XXX' \
     -F 'movie=http://www.imdb.com/title/tt0848228/' \
        'https://graph.facebook.com/me/stampedapp:stamp'

#We will be POSTing to Open Graph whenever a user stamps an entity.  The entity link will be hosted by stamped.com (the specifics of which are still under development), but for the purposes of this example, I'm using a standard IMDB page as a stand-in.

curl -F 'access_token=XXX' \
     -F 'movie=http://www.imdb.com/title/tt0848228/' \
     -F 'user_generated_image=https://s3.amazonaws.com/stamped.com.static.temp/017d4f29a57170f153fcdfc037b14643-1334427351.jpg' \
        'https://graph.facebook.com/me/stampedapp:stamp'

