(ns train-crawler.core
  (:use [train_crawler.crawler]
        [train_crawler.kafka_handler])
  (:require [clojure.data.json :as json]))

(def ^:private config (read-string (slurp "config.clj")))

(def sleeptime (if (nil? (:interval config)) 60000 (:interval config)))

(defn -main
  "I don't do a whole lot."
  []
  (while true
    (do
      (try (do
             (println "Start requesting...")
             (let [train-conns  (get-train-conns)]
               (println "received train connections, write to kafka.")
               (write-to-kafka (json/write-str train-conns))
               (println "wrote train connections to kafka")))
        (catch Exception e (str "caught exception: " (.getMessage e))))
      (Thread/sleep sleeptime))))


