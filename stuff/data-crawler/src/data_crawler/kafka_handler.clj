  (ns data_crawler.kafka_handler
    (:import (kafka.consumer Consumer ConsumerConfig KafkaStream)
             (kafka.producer KeyedMessage ProducerConfig)
             (kafka.javaapi.producer Producer)
             (java.util Properties)
             (java.util.concurrent Executors))
    (:gen-class))


  (def ^:private config (:kafka (read-string (slurp "config.clj"))))

  (defn- create-producer
    "Creates a producer that can be used to send a message to Kafka"
    [brokers]
    (let [props (Properties.)]
      (doto props
        (.put "metadata.broker.list" brokers)
        (.put "serializer.class" "kafka.serializer.StringEncoder")
        (.put "request.required.acks" "1"))
      (Producer. (ProducerConfig. props))))

  (defn- send-to-producer
    "Send a string message to Kafka"
    [producer topic message]
    (let [data (KeyedMessage. topic nil message)]
      (.send producer data)))



  (def ^:private producer (create-producer (:brokers config)))

  (defn write-to-queue
    "write a message to kafka"
    [topic message]
    (try
      (send-to-producer producer topic message)
      (catch Exception e (str "caught exception: " (.getMessage e)))))
