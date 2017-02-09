(ns data_crawler.weather_crawler
  (:use [data_crawler.kafka_handler]
        [hickory.core])
  (:require [hickory.select :as s]
            [clj-http.client :as client]
            [clojure.string :as string]
            [clj-time.core :as t]
            [clj-time.local :as l]
            [clojure.data.json :as json]
            [clj-time.coerce :as c]
            [clj-time.predicates :as pr]))

(def ^:private config (:weather (read-string (slurp "config.clj"))))
(def ^:private cities (:cities config))


(defn- get-weather-data [city]
  (slurp (str "http://api.openweathermap.org/data/2.5/weather?q=" city ",de&units=metric&APPID=" (:apiKey config))))


(def ^:private pull-sleeptime (if (nil? (:pullInterval config)) 60000 (:pullInterval config)))
(def ^:private push-sleeptime (if (nil? (:pushInterval config)) 60000 (:pushInterval config)))
(def ^:private topic (if (nil? (:topic config)) "weather-news" (:topic config)))
(def ^:private forecast-topic (if (nil? (:forecast-topic config)) "weather-forecast" (:forecast-topic config)))
(def ^:private data (ref {} :meta {}))
(def ^:private forecast-data (ref {} :meta {}))


(defn- try-get-weather-data [city]
  (try
    (do
      (println (str "start fetching weather data for '" city "'"))
      (let [res (get-weather-data city)]
        (println (str "received weather data for '" city "'"))
        (dosync
          (ref-set data (assoc @data city (json/read-str res))))))
    (catch Exception e (str "caught exception: " (.getMessage e)))))



(defn- get-forecast [city]
  (slurp (str "http://api.openweathermap.org/data/2.5/forecast?q=" city ",de&units=metric&APPID=" (:apiKey config))))



(defn- try-get-forecast-data [city]
  (try
    (do
      (println (str "start fetching forecast weather data for '" city "'"))
      (let [fc (get-forecast city)
            pure-weather-data (get (json/read-str fc) "list")
            weather-data-of-midday (filterv #(= 15 (  t/hour (c/from-long (* 1000 (get % "dt"))))) pure-weather-data)]
        (println (str "received forecast weather data for '" city "'"))
        (dosync
          (ref-set forecast-data (assoc @forecast-data city weather-data-of-midday)))))
    (catch Exception e (str "caught exception: " (.getMessage e)))))


(defn start-weather-producers
  "starts two threads for grapping data from openweathermap.org and push infos to kafka with different intervals."
  []
  (.start (Thread. (fn []
                     (while true
                       (doseq [c cities]
                         (try-get-weather-data c)
                         (try-get-forecast-data c))
                       (Thread/sleep pull-sleeptime)))))
  (.start (Thread. (fn []
                     (while true
                       (doseq [c cities]
                         (when-not (and (nil? (get @data c)) (nil? (get @forecast-data c)))
                           (write-to-kafka topic (json/write-str {:location (.toLowerCase c)
                                                                        :data (get @data c)}))
                           (write-to-kafka forecast-topic (json/write-str {:location (.toLowerCase c)
                                                                                 :data (get @forecast-data c)}))
                           (println (str "wrote weather data of '" c "' to kafka"))))
                        (Thread/sleep push-sleeptime))))))





