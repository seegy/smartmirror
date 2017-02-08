{
  :train {

           :topic "train-news"
           :pullInterval 60000
           :pushInterval 10000
           }
  :kafka {
           :brokers "localhost:9092"
           :zookeeper "localhost:2181"

           }
  :weather {
             :topic "weather-news-"
             :pullInterval 360000
             :pushInterval 10000
             :apiKey ""
             :cities ["Giessen" "Frankfurt"]
             }
  }
