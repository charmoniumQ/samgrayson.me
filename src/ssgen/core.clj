(ns ssgen.core
  (:require [stasis.core]))

(def server
  (stasis.core/serve-pages #(load-file "content/pages.clj")))
