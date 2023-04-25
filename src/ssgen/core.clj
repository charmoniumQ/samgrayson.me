(ns ssgen.core
  (:require [stasis.core]))

(def server
  (stasis.core/serve-pages #(load-file "content/pages.clj")))

(defn export []
  (let [pages (load-file "content/pages.clj")
        target-dir "docs/"
        date-str (let [sdf (new java.text.SimpleDateFormat "yyyy-MM-dd'T'HH:mm:ss.SSSXXX")]
                    (.setTimeZone sdf (java.util.TimeZone/getTimeZone "GMT"))
                    (.format sdf (new java.util.Date)))
        ]
    (doseq [[uri pageish] pages] (println uri))
    (stasis.core/empty-directory! target-dir)
    (stasis.core/export-pages pages target-dir)

                                        ; Ugly hack to work around https://github.com/magnars/stasis/issues/23
    (println "/CNAME")
    (spit (clojure.java.io/file target-dir "CNAME") "samgrayson.me")

    (println "/.nojekyll")
    (spit (clojure.java.io/file target-dir ".nojekyll") "")

    (println "/.date-updated")
    (spit (clojure.java.io/file target-dir ".date-updated") date-str)

    (println "/.well-known/matrix/server")
    (.mkdir (clojure.java.io/file target-dir ".well-known"))
    (.mkdir (clojure.java.io/file target-dir ".well-known/matrix"))
    (spit (clojure.java.io/file target-dir ".well-known/matrix/server") "{\"m.server\":\"matrix.samgrayson.me:443\"}")

    (println "/.well-known/matrix/client")
    (spit (clojure.java.io/file target-dir ".well-known/matrix/client") "{\"default_server_config\":{\"m.homeserver\":{\"base_url\":\"https://samgrayson.me\"},\"m.identity_server\":{\"base_url\": \"https://vector.im\"}}}")

                                        ; Bump index.html to trigger update
                                        ; https://stackoverflow.com/questions/20422279/github-pages-are-not-updating
    (spit (clojure.java.io/file target-dir "index.html") (apply str ["<!--" date-str "-->"]) :append true)

    (println "Donezo")))
