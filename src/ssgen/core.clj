(ns ssgen.core
  (:require [stasis.core]))

(def server
  (stasis.core/serve-pages #(load-file "content/pages.clj")))

(defn export []
  (let [pages (load-file "content/pages.clj")
        target-dir "docs/"]
    (doseq [[uri pageish] pages] (println uri))
    (stasis.core/empty-directory! target-dir)
    (stasis.core/export-pages pages target-dir)

                                        ; Ugly hack to work around https://github.com/magnars/stasis/issues/23
    (println "/CNAME")
    (spit (clojure.java.io/file target-dir "CNAME") "samgrayson.me")
    (println "/.well-known/matrix/server")
    (.mkdir (clojure.java.io/file target-dir ".well-known"))
    (.mkdir (clojure.java.io/file target-dir ".well-known/matrix"))
    (spit (clojure.java.io/file target-dir ".well-known/matrix/server") "{\"m.server\": \"matrix.samgrayson.me:443\"}")

                                        ; Bump index.html to trigger update
                                        ; https://stackoverflow.com/questions/20422279/github-pages-are-not-updating
    (spit (clojure.java.io/file target-dir "index.html") (apply str ["<!--" (rand-int 1000) "-->"]) :append true)

    (println "Donezo")))
