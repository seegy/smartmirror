(ns data_crawler.train_crawler
  (:use [data_crawler.redis_handler])
  (:require [google-apps-clj.credentials :as gauth]
            [google-apps-clj.google-calendar :refer :all]
            ))

(clojure.edn/read-string (slurp "resources/google-creds.edn"))

(gauth/get-auth-map (clojure.edn/read-string (slurp "resources/google-creds.edn")) ["https://www.googleapis.com/auth/calendar"])

#_(let [scopes [com.google.api.services.calendar.CalendarScopes/CALENDAR]
      creds (gauth/default-credential scopes)]
  (list-day-events creds "2017-04-21" "+02"))


;4/rgm34khpuH2JeVIKUrdEbxysdqKaprXi2V6ap3-Ggqg
