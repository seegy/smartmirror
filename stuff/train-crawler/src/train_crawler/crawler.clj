(ns train_crawler.crawler)


(use 'hickory.core)
(require '[hickory.select :as s])
(require '[clj-http.client :as client])

(require '[clojure.string :as string])

(require '[clj-time.core :as t])
(require '[clj-time.local :as l])

(def ^:private weekdays ["So" "Mo" "Di" "Mi" "Do" "Fr" "Sa" "So"])


(defn- get-datetime
  "delivers datetime of current day in bahn.de format"
  []
  (let [ln (l/local-now)
        wd (get weekdays (t/day-of-week (l/local-now)))]
    (str "date=" wd "%2C+" (t/day ln) "."  (t/month ln) "." (t/year ln) "&time=010%3A00")))


;(defn get-datetime [] "date=Mo%2C+06.02.17&time=010%3A00")
(def ^:private url (str "https://reiseauskunft.bahn.de/bin/query.exe/dn?revia=yes&existOptimizePrice=1&country=DEU&dbkanal_007=L01_S01_D001_KIN0001_qf-bahn-svb-kl2_lz03&start=1&REQ0JourneyStopsS0A=1&S=Gie%C3%9Fen+Licher+Str&REQ0JourneyStopsSID=A%3D1%40O%3DGie%C3%9Fen+Licher+Str%40X%3D8697243%40Y%3D50581663%40U%3D80%40L%3D008003674%40B%3D1%40p%3D1485903566%40&Z=Frankfurt%28Main%29West&REQ0JourneyStopsZID=&" (get-datetime) "&timesel=depart&returnDate=&returnTime=&returnTimesel=depart&optimize=0&auskunft_travelers_number=1&tariffTravellerType.1=E&tariffTravellerReductionClass.1=0&tariffClass=2&rtMode=DB-HYBRID&externRequest=yes&HWAI=JS%21js%3Dyes%21ajax%3Dyes%21"))


(defn get-train-conns
  "starts an request and get train connections"
  []
  (let [site-htree (->  (client/get url) :body parse as-hickory)
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

