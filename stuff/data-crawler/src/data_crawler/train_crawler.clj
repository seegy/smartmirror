(ns data_crawler.train_crawler
  (:use [data_crawler.redis_handler]
        [hickory.core])
  (:require [hickory.select :as s]
            [clj-http.client :as client]
            [clojure.string :as string]
            [clj-time.core :as t]
            [clj-time.local :as l]
            [clojure.data.json :as json]))

(def ^:private weekdays ["So" "Mo" "Di" "Mi" "Do" "Fr" "Sa" "So"])


(def ^:private config (:train (read-string (slurp "config.clj"))))

(defn- get-datetime
  "delivers datetime of current day in bahn.de format"
  []
  (let [ln (t/plus (l/local-now) (t/minutes 15))
        wd (get weekdays (t/day-of-week (l/local-now)))]
    (str "date=" wd "%2C+" (t/day ln) "."  (t/month ln) "." (t/year ln) "&time=0" (t/hour ln) "%3A" (t/minute ln))))


;(defn get-datetime [] "date=Mo%2C+06.02.17&time=010%3A00")
;(defn- url [] (str "https://reiseauskunft.bahn.de/bin/query.exe/dn?revia=yes&existOptimizePrice=1&country=DEU&dbkanal_007=L01_S01_D001_KIN0001_qf-bahn-svb-kl2_lz03&start=1&REQ0JourneyStopsS0A=1&S=Gie%C3%9Fen+Licher+Str&REQ0JourneyStopsSID=A%3D1%40O%3DGie%C3%9Fen+Licher+Str%40X%3D8697243%40Y%3D50581663%40U%3D80%40L%3D008003674%40B%3D1%40p%3D1485903566%40&Z=Frankfurt%28Main%29West&REQ0JourneyStopsZID=&" (get-datetime) "&timesel=depart&returnDate=&returnTime=&returnTimesel=depart&optimize=0&auskunft_travelers_number=1&tariffTravellerType.1=E&tariffTravellerReductionClass.1=0&tariffClass=2&rtMode=DB-HYBRID&externRequest=yes&HWAI=JS%21js%3Dyes%21ajax%3Dyes%21"))


(defn get-train-conns
  "starts an request and get train connections"
  [url]
  (let [site-htree (->  (client/get (str url "&" (get-datetime))) :body parse as-hickory)
        train-times (->>
                      (s/select (s/child (s/class "scheduledCon") ; sic
                                         (s/child (s/tag "tr"))
                                         (s/class "time")
                                         )
                                site-htree)
                      (map :content)
                      (map (fn [[a b]] [a (first (:content b))]))
                      (filter (fn[[a _]] (and (not (nil? a)) (not= "\n" a)))))
        train-conns (map (fn [a b ] [a b])  train-times  (drop  1 train-times))
        details (->>
                  (s/select (s/child (s/class "scheduledCon") ; sic
                                     (s/child (s/class "buttonLine"))
                                     (s/child (s/tag "td"))
                                     (s/child (s/class "iconLink"))
                                     )
                            site-htree)
                  (map :attrs))
        detail-responses (->> details
                              (map :rel)
                              (map #(string/split % #";"))
                              (map first)
                              (map #(string/replace % #"(\]|\})" ""))
                              (map #(string/replace % #"\[" "!"))
                              (map #(string/replace % #"\{" "\\$"))
                              (map #(string/replace % #":" "="))
                              (map #(str % "!"))
                              (map #(str (:href (first details)) % "&ajax=1"))
                              (map #(-> (client/get %) :body parse as-hickory)))
        detail-connections (map #(->> (s/select (s/child (s/and (s/or (s/class "first") (s/class "last"))
                                                                (s/tag :tr)))
                                                %)
                                      (map (fn [tr] {:station (-> (s/select (s/child (s/and (s/tag :td) (s/class "station"))) tr) first :content first str (string/replace #"\n" "") string/trim)
                                                     :time (-> (s/select (s/child (s/and (s/tag :td) (s/class "time"))) tr) first :content first str (string/replace #"(\n|ab|an)" "") string/trim)
                                                     :delay (-> (s/select (s/child (s/and (s/tag :td) (s/class "time")) (s/tag :span)) tr) first :content first str (string/replace #"\n" "") string/trim)}))
                                      ((fn[d] (map (fn [a b] [a b]) d (drop 1 d))))
                                      (filter (fn [a] (every? (fn[b] (some (fn [c] (not (string/blank? c))) (vals b))) a)))
                                      (keep-indexed (fn [a b](if (even? a) b nil))))
                                detail-responses)]
    detail-connections))




(def ^:private pull-sleeptime (if (nil? (:pullInterval config)) 60000 (:pullInterval config)))
(def ^:private push-sleeptime (if (nil? (:pushInterval config)) 60000 (:pushInterval config)))
(def ^:private topic (if (nil? (:topic config)) "train-news" (:topic config)))
(def ^:private data (ref {} :meta {}))


(defn- try-get-conns []
  (try (doseq [connections (:connections config)]
         (println "Start requesting...")
         (let [train-conns  (get-train-conns (:url connections))]
           (println "received train connections, write to queue.")
           (dosync
             (ref-set data (assoc @data (select-keys connections [:from :to]) train-conns)))))
    (catch Exception e (str "caught exception: " (.getMessage e)))))



(defn start-train-producer
  "starts two threads for grapping data from bahn.de and push infos to queue with different intervals."
  []
  (.start (Thread. (fn []
                     (while true
                       (try-get-conns)
                       (Thread/sleep pull-sleeptime)))))
  (.start (Thread. (fn []
                     (while true
                       (when-not (empty? @data)
                         (doseq [ [id dat] @data]
                           (write-to-queue topic (json/write-str (assoc id :data dat)))
                           (println "wrote train connections to queue")))
                       (Thread/sleep push-sleeptime))))))




