(ns data_crawler.redis_handler
  (:require [taoensso.carmine :as car :refer (wcar)]))


(def ^:private config (:redis (read-string (slurp "config.clj"))))


(def ^:private server1-conn {:pool {} :spec config}) ; See `wcar` docstring for opts
(defmacro wcar* [& body] `(car/wcar server1-conn ~@body))

;(wcar* (car/ping)) ; => "PONG" (1 command -> 1 reply)
;(wcar* (car/publish "weather-news" "Hello to foobar!"))

(defn write-to-queue
    "write a message to redis"
    [channel message]
    (try
      (wcar* (car/publish channel message))
      (catch Exception e (println (str "caught exception: " (.getMessage e))))))

;(write-to-redis "weather-news" "Hello to foofdgsdgbar!")
