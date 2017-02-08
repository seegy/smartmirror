(ns data_crawler.core
  (:use [data_crawler.train_crawler]
        [data_crawler.weather_crawler]))


(defn -main
  "I don't do a whole lot."
  []
  (start-train-producer)
  (start-weather-producers))


