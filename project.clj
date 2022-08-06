(defproject ssgen "0.1.0-SNAPSHOT"
  :description "This is the configuration that generates my wesbsite."
  :url "http://github.com/charmoniumQ/samgrayson.me"
  :license {:name "MIT"
            :url "https://opensource.org/licenses/MIT"}
  :dependencies [
                 [org.clojure/clojure "1.10.3"]
                 [selmer "1.12.53"]
                 [stasis "2.5.0"]
                 [ring "1.8.2"]
                 ]
  :ring {:handler ssgen.core/server}
  :main ^:skip-aot ssgen.core
  :target-path "target/%s"
  :profiles {:dev {:plugins [[lein-ring "0.12.5"]]}}
  ;:profiles {:uberjar {:aot :all :jvm-opts ["-Dclojure.compiler.direct-linking=true"]}}
  )

;(setq cider-lein-command (car (last (split-string (shell-command-to-string "nix develop --command which lein")))))
