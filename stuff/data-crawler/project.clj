(defproject data-crawler "0.1.0-SNAPSHOT"
  :description "FIXME: write description"
  :url "http://example.com/FIXME"
  :license {:name "Eclipse Public License"
            :url "http://www.eclipse.org/legal/epl-v10.html"}
  :dependencies [[org.clojure/clojure "1.8.0"]
                 [org.apache.kafka/kafka_2.9.2 "0.8.1.1" :exclusions [javax.jms/jms
                                                                      com.sun.jdmk/jmxtools
                                                                      com.sun.jmx/jmxri]]
                 [hickory "0.7.0"]
                 [clj-http "2.3.0"]
                 [clj-time "0.13.0"]
                 [org.clojure/data.json "0.2.6"]]
    :main data_crawler.core)
