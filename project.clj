(defproject ssgen "0.1.0-SNAPSHOT"
  :description "This is the configuration that generates my wesbsite."
  :url "http://github.com/charmoniumQ/samgrayson.me"
  :license {:name "MIT"
            :url "https://opensource.org/licenses/MIT"}
  :dependencies [[org.clojure/clojure "1.11.1"]
                 [selmer "1.12.53"]
                 [stasis "2.5.1"]
                 [ring "1.9.5"]
                 [clj-html-compressor "0.1.1"]
                 [org.clojure/tools.trace "0.7.11"]
                 [com.yahoo.platform.yui/yuicompressor "2.4.8"]
                 [clj-commons/clj-yaml "0.7.109"]]
  :ring {:handler ssgen.core/server}
  :target-path "target/%s"
  :aliases {"build" ["run" "-m" "ssgen.core/export"]
            "serve" ["ring" "server"]}
  :profiles {:dev {:plugins [[lein-ring "0.12.5"]
                             [lein-ancient "1.0.0-RC3"]]}})

;(setq cider-lein-command (car (last (split-string (shell-command-to-string "nix develop --command which lein")))))
