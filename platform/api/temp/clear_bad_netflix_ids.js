
var dryRun = typeof trust_me_im_a_doctor === "undefined";

var query = {"sources.netflix_id" : { "$regex" : "^\\d*$"}};
var netflixUpdate = {"$unset" : {
    "sources.netflix_id" : 1,
    "sources.netflix_instant_available_until" : 1,
    "sources.netflix_is_instant_available" : 1,
    "sources.netflix_source" : 1,
    "sources.netflix_timestamp" : 1,
    "sources.netflix_url" : 1,
    }
};

function printNetflixId(entity) {
    print(entity["sources"]["netflix_id"]);
}


if (dryRun)
    db.entities.find(query).forEach(printNetflixId);
else
    db.entities.update(query, netflixUpdate, false, true);
