(ns ssgen.core
  (:require [stasis.core]))

(def server
  (stasis.core/serve-pages #(load-file "content/pages.clj")))

(defn export []
  (let [pages #(load-file "content/pages.clj")
        target-dir "docs"]
    (stasis.core/empty-directory! target-dir)
    (stasis.core/export-pages pages target-dir)))
