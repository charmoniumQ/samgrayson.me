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

    (println "Donezo")))
